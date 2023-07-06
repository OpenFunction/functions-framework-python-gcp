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
import uvicorn

from functions_framework import constants
from functions_framework.context.function_context import HTTPRoute
from functions_framework.context.runtime_context import RuntimeContext
from functions_framework.triggers.http_trigger import create_app
from functions_framework.triggers.http_trigger._http import create_server
from functions_framework.triggers.trigger import TriggerHandler


class HTTPTriggerHandler(TriggerHandler):
    """Handle http trigger."""
    def __init__(self, port, trigger: HTTPRoute, source=None, target=None, user_function=None, debug=False):
        self.port = trigger.port if trigger.port else port
        self.source = source
        self.target = target
        self.trigger = trigger
        self.hostname = trigger.hostname
        self.route_rules = trigger.rules
        self.user_function = user_function
        self.debug = debug
        if self.port == 0:
            self.port = constants.DEFAULT_HTTP_APP_PORT

    def start(self, context: RuntimeContext, logger=None):
        if not self.trigger:
            raise Exception("No trigger specified for HTTPTriggerHandler")

        app = create_app(context, self.target, self.source, logger)
        create_server(app, self.debug).run("0.0.0.0", self.port)



