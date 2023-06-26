import logging
from copy import deepcopy
from cloudevents.sdk.event import v1

from functions_framework.context.function_context import DaprTrigger
from functions_framework.context.runtime_context import RuntimeContext
from functions_framework.context.user_context import UserContext
from functions_framework.triggers.trigger import TriggerHandler

from dapr.ext.grpc import App, BindingRequest


class DaprTriggerHandler(TriggerHandler):
    def __init__(self, port, app: App = None, triggers: [DaprTrigger] = None, user_function=None):
        self.port = port
        self.triggers = triggers
        self.app = app
        self.user_function = user_function

    def start(self, context: RuntimeContext, logger=None):
        if not self.triggers:
            raise Exception("No triggers specified for DaprTriggerHandler")

        for trigger in self.triggers:
            if trigger.component_type.startswith("bindings"):
                @self.app.binding(trigger.name)
                def binding_handler(request: BindingRequest):
                    rt_ctx = deepcopy(context)
                    user_ctx = UserContext().__int__(runtime_context=rt_ctx, binding_request=request, logger=logger)
                    logging.basicConfig(level=logging.INFO)
                    logging.info('Received Message : ' + request.text())
                    self.user_function(user_ctx)

            if trigger.component_type.startswith("pubsub"):
                @self.app.subscribe(pubsub_name=trigger.name, topic=trigger.topic)
                def topic_handler(event: v1.Event):
                    rt_ctx = deepcopy(context)
                    user_ctx = UserContext().__int__(runtime_context=rt_ctx, topic_event=event, logger=logger)
                    logging.basicConfig(level=logging.INFO)
                    logging.info('Received Message : ' + event.data.__str__())
                    self.user_function(user_ctx)
