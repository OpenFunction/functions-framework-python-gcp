# Copyright 2023 The OpenFunction Authors.
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
import io
import json
import logging
import sys

import flask

from cloudevents.http import from_http

from functions_framework.exceptions import (
    EventConversionException,
    FunctionsFrameworkException,
)
from functions_framework.openfunction import dapr_output_middleware
from functions_framework.runner import Runner

MAX_CONTENT_LENGTH = 10 * 1024 * 1024

_FUNCTION_STATUS_HEADER_FIELD = "X-Google-Status"
_CRASH = "crash"

_CLOUDEVENT_MIME_TYPE = "application/cloudevents+json"


class _LoggingHandler(io.TextIOWrapper):
    """Logging replacement for stdout and stderr in GCF Python 3.7."""

    def __init__(self, level, stderr=sys.stderr):
        io.TextIOWrapper.__init__(self, io.StringIO(), encoding=stderr.encoding)
        self.level = level
        self.stderr = stderr

    def write(self, out):
        payload = dict(severity=self.level, message=out.rstrip("\n"))
        return self.stderr.write(json.dumps(payload) + "\n")


def setup_logging():
    logging.getLogger().setLevel(logging.INFO)
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.NOTSET)
    info_handler.addFilter(lambda record: record.levelno <= logging.INFO)
    logging.getLogger().addHandler(info_handler)

    warn_handler = logging.StreamHandler(sys.stderr)
    warn_handler.setLevel(logging.WARNING)
    logging.getLogger().addHandler(warn_handler)


def setup_logging_level(debug):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)


def _http_view_func_wrapper(function, request):
    def view_func(path):
        return function(request._get_current_object())

    return view_func


def _run_cloud_event(function, request):
    data = request.get_data()
    event = from_http(request.headers, data)
    function(event)



def read_request(response):
    """
    Force the framework to read the entire request before responding, to avoid
    connection errors when returning prematurely.
    """

    flask.request.get_data()
    return response


def crash_handler(e):
    """
    Return crash header to allow logging 'crash' message in logs.
    """
    return str(e), 500, {_FUNCTION_STATUS_HEADER_FIELD: _CRASH}


class LazyWSGIApp:
    """
    Wrap the WSGI app in a lazily initialized wrapper to prevent initialization
    at import-time
    """

    def __init__(self, target=None, source=None, signature_type=None, func_context=None, debug=False):
        # Support HTTP frameworks which support WSGI callables.
        # Note: this ability is currently broken in Gunicorn 20.0, and
        # environment variables should be used for configuration instead:
        # https://github.com/benoitc/gunicorn/issues/2159
        self.target = target
        self.source = source
        self.signature_type = signature_type
        self.func_context = func_context
        self.debug = debug

        # Placeholder for the app which will be initialized on first call
        self.app = None

    def __call__(self, *args, **kwargs):
        if not self.app:
            self.app = Runner(self.target, self.source, self.signature_type, self.func_context, self.debug)
        return self.app(*args, **kwargs)


app = LazyWSGIApp()


class DummyErrorHandler:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return self


errorhandler = DummyErrorHandler()
