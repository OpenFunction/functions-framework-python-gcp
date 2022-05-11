OPEN_FUNC_BINDING = "bindings"
OPEN_FUNC_TOPIC = "pubsub"

KNATIVE_RUNTIME_TYPE = "Knative"
ASYNC_RUNTIME_TYPE = "Async"


class FunctionContext(object):
    """OpenFunction's serving context."""
    
    def __init__(self, name="", version="", runtime="", inputs=None, outputs=None, port=8080):
        self.name = name
        self.version = version
        self.runtime = runtime
        self.inputs = inputs
        self.outputs = outputs
        self.port = port

    @staticmethod
    def from_json(json_dct):
        name = json_dct.get('name')
        version = json_dct.get('version')
        runtime = json_dct.get('runtime')
        inputs_list = json_dct.get('inputs')
        outputs_list = json_dct.get('outputs')

        inputs = None
        if inputs_list:
            inputs = {}
            for k, v in inputs_list.items():
                input = Component.from_json(v)
                inputs[k] = input

        outputs = None
        if outputs_list:
            outputs = {}
            for k, v in outputs_list.items():
                output = Component.from_json(v)
                outputs[k] = output
                
        return FunctionContext(name, version, runtime, inputs, outputs)


class Component(object):
    """Components for inputs and outputs."""

    def __init__(self, uri="", componentName="", componentType="", metadata=None, operation=""):
        self.uri = uri
        self.component_name = componentName
        self.component_type = componentType
        self.metadata = metadata
        self.operation = operation

    def get_type(self):
        type_split = self.component_type.split(".")
        if len(type_split) > 1:
            t = type_split[0]
        if t == OPEN_FUNC_BINDING or t == OPEN_FUNC_TOPIC:
            return t

        return ""

    def __str__(self):
        return "{uri: %s, component_name: %s, component_type: %s, operation: %s, metadata: %s}" % (
            self.uri,
            self.component_name,
            self.component_type,
            self.operation,
            self.metadata
        )

    @staticmethod
    def from_json(json_dct):
        uri = json_dct.get('uri') or ''
        component_name = json_dct.get('componentName') or ''
        metadata = json_dct.get('metadata')
        component_type = json_dct.get('componentType') or ''
        operation = json_dct.get('operation') or ''
        return Component(uri, component_name, component_type, metadata, operation)