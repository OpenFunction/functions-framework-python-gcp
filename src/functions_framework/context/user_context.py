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
import copy
import json

from dapr.clients import DaprClient

from functions_framework import constants
from functions_framework.context.runtime_context import RuntimeContext
from functions_framework.exceptions import exception_handler
from functions_framework.openfunction.function_out import FunctionOut


class UserContext(object):
    """Context for user."""

    def __init__(self, runtime_context: RuntimeContext = None,
                 binding_request=None, topic_event=None, http_request=None, logger=None):
        self.runtime_context = runtime_context
        self.logger = logger
        self.out = FunctionOut(0, None, "", {})
        self.dapr_client = None
        self.__binding_request = binding_request
        self.__topic_event = topic_event
        self.__http_request = http_request
        self.__init_dapr_client()

    def __init_dapr_client(self):
        if not self.dapr_client:
            self.dapr_client = DaprClient()

    def __init_logger(self):
        if self.logger:
            self.logger.name = __name__

    def get_binding_request(self):
        return copy.deepcopy(self.__binding_request)

    def get_topic_event(self):
        return copy.deepcopy(self.__topic_event)

    def get_http_request(self):
        return self.__http_request

    @exception_handler
    def send(self, output_name, data):
        """Send data to specify output component.
        Args:
            data: Bytes or str to send.
            output_name: A string of designated output name. Only send this output if designated.
        Returns:
            Response from dapr.
        """
        outputs = self.runtime_context.get_outputs()
        resp = None

        if not outputs:
            raise Exception("No outputs found.")

        if output_name not in outputs:
            raise Exception("No output named {} found.".format(output_name))

        target = outputs[output_name]
        if target.component_type.startswith(constants.DAPR_BINDING_TYPE):
            resp = self.dapr_client.invoke_binding(target.component_name, target.operation, data, target.metadata)
        elif target.component_type.startswith(constants.DAPR_PUBSUB_TYPE):
            data = json.dumps(data)
            resp = self.dapr_client.publish_event(
                target.component_name, target.topic, data,
                data_content_type=constants.DEFAULT_DATA_CONTENT_TYPE, publish_metadata=target.metadata)

        return resp
