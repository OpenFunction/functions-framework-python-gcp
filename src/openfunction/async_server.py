from dapr.ext.grpc import App, BindingRequest
from cloudevents.sdk.event import v1
from openfunction.function_context import OPEN_FUNC_BINDING, OPEN_FUNC_TOPIC
from openfunction.function_runtime import OpenFunctionRuntime

class AsyncApp(object):
    """Init async server with dapr server."""

    def __init__(self, func_context):
        """Inits async server.
        Args:
            func_context: OpenFunction context
        """
        self.ctx = OpenFunctionRuntime.parse(func_context)
        self.app = App()


    def bind(self, function): 
        """Bind user function with input binding/subscription.
        Args:
            function: user function
        """
        for input in self.ctx.inputs.values():
            type = input.get_type()
            if type == OPEN_FUNC_BINDING:
                @self.app.binding(input.component_name)
                def binding(request: BindingRequest):
                    function(self.ctx, request.data)
            elif type == OPEN_FUNC_TOPIC:
                @self.app.subscribe(pubsub_name=input.component_name, topic=input.uri, metadata=input.metadata)
                def mytopic(event: v1.Event) -> None:
                    function(self.ctx, bytes(event.data))