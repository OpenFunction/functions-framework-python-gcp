# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import io
import json
import logging
import os.path
import pathlib
import sys

from copy import deepcopy

import flask
import werkzeug

from functions_framework import _function_registry
from functions_framework.context.runtime_context import RuntimeContext
from functions_framework.context.user_context import UserContext
from functions_framework.exceptions import MissingSourceException

_FUNCTION_STATUS_HEADER_FIELD = "X-OpenFunction-Status"
_CRASH = "crash"


class _LoggingHandler(io.TextIOWrapper):
    """Logging replacement for stdout and stderr in GCF Python 3.7."""

    def __init__(self, level, stderr=sys.stderr):
        io.TextIOWrapper.__init__(self, io.StringIO(), encoding=stderr.encoding)
        self.level = level
        self.stderr = stderr

    def write(self, out):
        payload = dict(severity=self.level, message=out.rstrip("\n"))
        return self.stderr.write(json.dumps(payload) + "\n")


def cloud_event(func):
    """Decorator that registers cloudevent as user function signature type."""
    _function_registry.REGISTRY_MAP[
        func.__name__
    ] = _function_registry.CLOUDEVENT_SIGNATURE_TYPE

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def http(func):
    """Decorator that registers http as user function signature type."""
    _function_registry.REGISTRY_MAP[
        func.__name__
    ] = _function_registry.HTTP_SIGNATURE_TYPE

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def setup_logging():
    logging.getLogger().setLevel(logging.INFO)
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.NOTSET)
    info_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    logging.getLogger().addHandler(info_handler)

    warn_handler = logging.StreamHandler(sys.stderr)
    warn_handler.setLevel(logging.WARNING)
    logging.getLogger().addHandler(warn_handler)


def _http_view_func_wrapper(function, runtime_context: RuntimeContext, request, logger):
    @functools.wraps(function)
    def view_func(path):
        rt_ctx = deepcopy(runtime_context)
        user_ctx = UserContext(runtime_context=rt_ctx, http_request=request, logger=logger)
        return function(user_ctx)

    return view_func


def _configure_app(wsgi_app, runtime_context: RuntimeContext, function, logger):
    wsgi_app.url_map.add(
        werkzeug.routing.Rule("/", defaults={"path": ""}, endpoint="run")
    )
    wsgi_app.url_map.add(werkzeug.routing.Rule("/robots.txt", endpoint="error"))
    wsgi_app.url_map.add(werkzeug.routing.Rule("/favicon.ico", endpoint="error"))
    wsgi_app.url_map.add(werkzeug.routing.Rule("/<path:path>", endpoint="run"))
    wsgi_app.view_functions["run"] = _http_view_func_wrapper(function, runtime_context, flask.request, logger)
    wsgi_app.view_functions["error"] = lambda: flask.abort(404, description="Not Found")
    wsgi_app.after_request(read_request)


def read_request(response):
    """
    Force the framework to read the entire request before responding, to avoid
    connection errors when returning prematurely. Skipped on streaming responses
    as these may continue to operate on the request after they are returned.
    """

    if not response.is_streamed:
        flask.request.get_data()

    return response


def crash_handler(e):
    """
    Return crash header to allow logging 'crash' message in logs.
    """
    return str(e), 500, {_FUNCTION_STATUS_HEADER_FIELD: _CRASH}


def create_app(runtime_context: RuntimeContext = None, target=None, source=None, logger=None):
    _target = _function_registry.get_function_target(target)
    _source = _function_registry.get_function_source(source)

    # Set the template folder relative to the source path
    # Python 3.5: join does not support PosixPath
    template_folder = str(pathlib.Path(_source).parent / "templates")

    if not os.path.exists(_source):
        raise MissingSourceException(
            "File {source} that is expected to define function doesn't exist".format(
                source=_source
            )
        )

    source_module, spec = _function_registry.load_function_module(_source)

    # Create the application
    _app = flask.Flask(_target, template_folder=template_folder)
    _app.register_error_handler(500, crash_handler)
    global errorhandler
    errorhandler = _app.errorhandler

    # Handle legacy GCF Python 3.7 behavior
    if os.environ.get("ENTRY_POINT"):
        os.environ["FUNCTION_NAME"] = os.environ.get("K_SERVICE", _target)
        _app.make_response_original = _app.make_response

        def handle_none(rv):
            if rv is None:
                rv = "OK"
            return _app.make_response_original(rv)

        _app.make_response = handle_none

        # Handle log severity backwards compatibility
        sys.stdout = _LoggingHandler("INFO", sys.stderr)
        sys.stderr = _LoggingHandler("ERROR", sys.stderr)
        setup_logging()

    # Execute the module, within the application context
    with _app.app_context():
        spec.loader.exec_module(source_module)

    # Get the configured function signature type
    function = _function_registry.get_user_function(_source, source_module, _target)

    _configure_app(_app, runtime_context, function, logger)

    return _app


class LazyWSGIApp:
    """
    Wrap the WSGI app in a lazily initialized wrapper to prevent initialization
    at import-time
    """

    def __init__(self, target=None, source=None, signature_type=None):
        # Support HTTP frameworks which support WSGI callables.
        # Note: this ability is currently broken in Gunicorn 20.0, and
        # environment variables should be used for configuration instead:
        # https://github.com/benoitc/gunicorn/issues/2159
        self.target = target
        self.source = source
        self.signature_type = signature_type

        # Placeholder for the app which will be initialized on first call
        self.app = None

    def __call__(self, *args, **kwargs):
        if not self.app:
            self.app = create_app(self.target, self.source, self.signature_type)
        return self.app(*args, **kwargs)


app = LazyWSGIApp()


class DummyErrorHandler:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return self


errorhandler = DummyErrorHandler()
