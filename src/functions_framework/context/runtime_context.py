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
from functions_framework.context.function_context import FunctionContext, OpenFunctionTrigger


class RuntimeContext(object):
    """Context for runtime."""

    def __int__(self, context: FunctionContext = None):
        self.context = context
        self.request = None

    def has_dapr_trigger(self):
        """Check if the function has dapr trigger."""
        return self.context and self.context.dapr_triggers

    def has_http_trigger(self):
        """Check if the function has http trigger."""
        return self.context and self.context.http_trigger

    def get_dapr_triggers(self) -> [OpenFunctionTrigger]:
        """Get dapr triggers."""
        triggers = []
        for trigger in self.context.dapr_triggers:
            triggers.append(
                OpenFunctionTrigger(name=trigger.get('name'), topic=trigger.get('topic'), component_type=trigger.get('type'))
            )
        return triggers
