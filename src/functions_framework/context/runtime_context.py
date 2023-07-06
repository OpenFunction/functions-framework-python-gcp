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
from functions_framework.context.function_context import (
    Component,
    DaprTrigger,
    FunctionContext,
    HTTPRoute,
)


class RuntimeContext:
    """Context for runtime."""

    def __init__(self, context: FunctionContext = None, logger=None):
        self.context = context
        self.logger = logger

    def __init_logger(self):
        if self.logger:
            self.logger.name = __name__

    def has_http_trigger(self):
        """Check if the function has http trigger."""
        return self.context and self.context.http_trigger

    def get_dapr_triggers(self) -> [DaprTrigger]:
        """Get dapr trigger."""
        if self.context:
            return self.context.dapr_triggers
        else:
            return []

    def get_http_trigger(self) -> HTTPRoute:
        """Get http trigger."""
        if self.context:
            return self.context.http_trigger
        else:
            return None

    def get_outputs(self) -> [Component]:
        if self.context and self.context.outputs:
            return self.context.outputs
        else:
            return []
