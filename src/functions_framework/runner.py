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
import logging
import os

from dapr.ext.grpc import App

from functions_framework import _function_registry, log
from functions_framework.context.function_context import FunctionContext
from functions_framework.context.runtime_context import RuntimeContext
from functions_framework.exceptions import MissingSourceException
from functions_framework.triggers.dapr_trigger.dapr import DaprTriggerHandler
from functions_framework.triggers.http_trigger.http import HTTPTriggerHandler


class Runner:
    def __init__(self, context: FunctionContext, target=None, source=None,
                 host=None, port=None, debug=None, dry_run=None):
        self.target = target
        self.source = source
        self.context = context
        self.user_function = None
        self.request = None
        self.host = host
        self.port = port
        self.debug = debug
        self.dry_run = dry_run
        self.logger = None
        self.load_user_function()
        self.init_logger()

    def load_user_function(self):
        _target = _function_registry.get_function_target(self.target)
        _source = _function_registry.get_function_source(self.source)

        if not os.path.exists(_source):
            raise MissingSourceException(
                "File {source} that is expected to define function doesn't exist".format(
                    source=_source
                )
            )

        source_module, spec = _function_registry.load_function_module(_source)
        spec.loader.exec_module(source_module)

        self.user_function = _function_registry.get_user_function(_source, source_module, _target)

    def init_logger(self):
        level = logging.INFO
        if self.debug:
            level = logging.DEBUG
        self.logger = log.initialize_logger(__name__, level)

    def run(self):
        # convert to runtime context
        runtime_context = RuntimeContext(self.context, self.logger)

        _trigger = runtime_context.get_http_trigger()
        if _trigger:
            http_trigger = HTTPTriggerHandler(self.context.port, _trigger, self.source, self.target, self.user_function)
            http_trigger.start(runtime_context, logger=self.logger)

        _triggers = runtime_context.get_dapr_triggers()
        if _triggers:
            dapr_trigger = DaprTriggerHandler(self.context.port, _triggers, self.user_function)
            dapr_trigger.start(runtime_context, logger=self.logger)
