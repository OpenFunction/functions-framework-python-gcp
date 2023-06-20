import logging
from copy import deepcopy

from functions_framework.context.function_context import OpenFunctionTrigger
from functions_framework.context.runtime_context import RuntimeContext
from functions_framework.triggers.trigger import Trigger

from dapr.ext.grpc import App, BindingRequest


class DaprTrigger(Trigger):
    def __init__(self, port, app: App = None, triggers: [OpenFunctionTrigger] = None, user_function=None):
        self.port = port
        self.triggers = triggers
        self.app = app
        self.user_function = user_function

    def start(self, context: RuntimeContext):
        if not self.triggers:
            raise Exception("No triggers specified for DaprTrigger")

        for trigger in self.triggers:
            if trigger.component_type.startswith("bindings"):
                @self.app.binding(trigger.name)
                def binding_handler(request: BindingRequest):
                    ctx = deepcopy(context)
                    ctx.request = request
                    logging.basicConfig(level=logging.INFO)
                    logging.info('Received Message : ' + request.text())
                    self.user_function(ctx)
