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
from functions_framework.constants import DAPR_BINDING_TYPE, DAPR_PUBSUB_TYPE


class FunctionContext(object):
    """OpenFunction's serving context."""

    def __init__(self, name="", version="", dapr_triggers=None, http_trigger=None,
                 inputs=None, outputs=None, states=None,
                 pre_hooks=None, post_hooks=None, tracing=None, port=0):
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
        inputs_map = json_dct.get('inputs')
        outputs_map = json_dct.get('outputs')
        _dapr_triggers = json_dct.get('triggers', {}).get('dapr', [])
        http_trigger = json_dct.get('triggers', {}).get('http', None)
        states = json_dct.get('states', {})
        pre_hooks = json_dct.get('pre_hooks', [])
        post_hooks = json_dct.get('post_hooks', [])
        tracing = json_dct.get('tracing', {})
        port = json_dct.get('port', 0)

        inputs = None
        if inputs_map:
            inputs = {}
            for k, v in inputs_map.items():
                _input = Component.from_json(v)
                inputs[k] = _input

        outputs = None
        if outputs_map:
            outputs = {}
            for k, v in outputs_map.items():
                output = Component.from_json(v)
                outputs[k] = output

        dapr_triggers = []
        for trigger in _dapr_triggers:
            dapr_triggers.append(DaprTrigger.from_json(trigger))

        if http_trigger:
            http_trigger = HTTPRoute.from_json(http_trigger)

        return FunctionContext(name, version, dapr_triggers, http_trigger,
                               inputs, outputs, states, pre_hooks, post_hooks, tracing, port)


class Component(object):
    """Components for inputs and outputs."""

    def __init__(self, component_name="", component_type="", topic="", metadata=None, operation=""):
        self.topic = topic
        self.component_name = component_name
        self.component_type = component_type
        self.metadata = metadata
        self.operation = operation

    def get_type(self):
        type_split = self.component_type.split(".")
        if len(type_split) > 1:
            t = type_split[0]
            if t == DAPR_BINDING_TYPE or t == DAPR_PUBSUB_TYPE:
                return t

        return ""

    def __str__(self):
        return "{component_name: %s, component_type: %s, topic: %s, metadata: %s, operation: %s}" % (
            self.component_name,
            self.component_type,
            self.topic,
            self.metadata,
            self.operation
        )

    @staticmethod
    def from_json(json_dct):
        topic = json_dct.get('topic', '')
        component_name = json_dct.get('componentName', '')
        metadata = json_dct.get('metadata')
        component_type = json_dct.get('componentType', '')
        operation = json_dct.get('operation', '')
        return Component(component_name, component_type, topic, metadata, operation)


class HTTPRoute(object):
    """HTTP route."""

    def __init__(self, port=""):
        self.port = port

    def __str__(self):
        return "{port: %s}" % (
            self.port
        )

    @staticmethod
    def from_json(json_dct):
        port = json_dct.get('port', '')
        return HTTPRoute(port)


class DaprTrigger(object):

    def __init__(self, name, component_type, topic):
        self.name = name
        self.component_type = component_type
        self.topic = topic

    def __str__(self):
        return "{name: %s, component_type: %s, topic: %s}" % (
            self.name,
            self.component_type,
            self.topic
        )

    @staticmethod
    def from_json(json_dct):
        name = json_dct.get('name', '')
        component_type = json_dct.get('type', '')
        topic = json_dct.get('topic')
        return DaprTrigger(name, component_type, topic)
