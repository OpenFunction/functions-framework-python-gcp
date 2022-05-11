from abc import abstractmethod
import os

from dapr.clients import DaprGrpcClient
from dapr.conf import settings

from openfunction.function_context import FunctionContext

DAPR_GRPC_PORT = "DAPR_GRPC_PORT"
OPEN_FUNC_BINDING = "bindings"
OPEN_FUNC_TOPIC = "pubsub"


class OpenFunctionRuntime(object):
    """OpenFunction Runtime."""

    def __init__(self, context=None):
        """Inits OpenFunction Runtime.
        Args:
            context: OpenFunction context
        """
        self.context = context

    def __getattribute__(self, item):
        try:
            target = object.__getattribute__(self, item)
            return target
        except AttributeError:
            target = object.__getattribute__(self, "context")
            return getattr(target, item)

    def set_dapr_grpc_port(self):
        port = os.environ.get(DAPR_GRPC_PORT)
        if port:
            settings.DAPR_GRPC_PORT = port
    
    @staticmethod
    def parse(context: FunctionContext):
        return DaprRuntime(context)
    
    @abstractmethod
    def send(self, data, output):
        """send data to certain ouput binding or pubsub topic"""


class DaprRuntime(OpenFunctionRuntime): 
    """Dapr runtime derived from OpenFunctionRuntime."""

    def __init__(self, context=None):
        """Inits Dapr Runtime.
        Args:
            context: OpenFunction context
        """
        super().__init__(context)
        super().set_dapr_grpc_port()

        self.client = DaprGrpcClient()

    def send(self, data, output=None):
        """Inits Dapr Runtime.
        Args:
            data: Bytes or str to send.
            output: A string of designated output name. Only send this output if designated.
        Returns:
            A dict mapping keys to the corresponding dapr response. 
        """
        outputs = self.context.outputs
        filtered_outputs = {}
        responses = {}

        if output and output in outputs:
            filtered_outputs[output] = outputs[output]
        else:
            filtered_outputs = outputs
            
        for key, value in filtered_outputs.items():
            type = value.get_type()
            if type == OPEN_FUNC_BINDING:
                resp = self.client.invoke_binding(value.component_name, value.operation, data, value.metadata)
            elif type == OPEN_FUNC_TOPIC:
                resp = self.client.publish_event(value.component_name, value.uri, data, value.metadata)
            responses[key] = resp

        return responses
            
