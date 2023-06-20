OPEN_FUNC_BINDING = "bindings"
OPEN_FUNC_TOPIC = "pubsub"

KNATIVE_RUNTIME_TYPE = "knative"
ASYNC_RUNTIME_TYPE = "async"


class FunctionContext(object):
    """OpenFunction's serving context."""
    
    def __init__(self, name="", version="", dapr_triggers=None, http_trigger=None,
                 inputs=None, outputs=None, states=None,
                 pre_hooks=None, post_hooks=None, tracing=None, port=8080):
        self.name = name
        self.version = version
        self.dapr_triggers = dapr_triggers
        self.http_trigger = http_trigger
        self.inputs = inputs
        self.outputs = outputs
        self.states = states
        self.pre_hooks = pre_hooks
        self.post_hooks = post_hooks
        self.tracing = tracing
        self.port = port

    @staticmethod
    def from_json(json_dct):
        name = json_dct.get('name')
        version = json_dct.get('version')
        inputs_list = json_dct.get('inputs')
        outputs_list = json_dct.get('outputs')
        dapr_triggers = json_dct.get('triggers', {}).get('dapr', [])
        http_trigger = json_dct.get('triggers', {}).get('http', None)
        states = json_dct.get('states', {})
        pre_hooks = json_dct.get('pre_hooks', [])
        post_hooks = json_dct.get('post_hooks', [])
        tracing = json_dct.get('tracing', {})

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
        return FunctionContext(name, version, dapr_triggers, http_trigger,
                               inputs, outputs, states, pre_hooks, post_hooks, tracing)


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
        uri = json_dct.get('uri', '')
        component_name = json_dct.get('componentName', '')
        metadata = json_dct.get('metadata')
        component_type = json_dct.get('componentType', '')
        operation = json_dct.get('operation', '')
        return Component(uri, component_name, component_type, metadata, operation)


class OpenFunctionTrigger(object):

    def __init__(self, name, component_type, topic):
        self.name = name
        self.component_type = component_type
        self.topic = topic

    @staticmethod
    def from_json(json_dct):
        name = json_dct.get('name', '')
        component_type = json_dct.get('type', '')
        topic = json_dct.get('topic')
        return OpenFunctionTrigger(name, component_type, topic)
