import os
from dapr.ext.grpc import App

from functions_framework import _function_registry
from functions_framework.exceptions import MissingSourceException
from functions_framework.context.function_context import FunctionContext
from functions_framework.context.runtime_context import RuntimeContext
from functions_framework.triggers.dapr_trigger.dapr import DaprTrigger


class Runner:
    def __init__(self, context: FunctionContext, target=None, source=None,
                 host=None, port=None, debug=None, dry_run=None):
        self.target = target
        self.source = source
        self.context = context
        self.user_function = None
        self.request = None
        self.app = App()
        self.load_user_function()

    def load_user_function(self):
        _target = _function_registry.get_function_target(self.target)
        _source = _function_registry.get_function_source(self.source)

        if not os.path.exists(_source):
            raise MissingSourceException(
                "File {source} that is expected to define function doesn't exist".format(
                    source=_source
                )
            )

        source_module, spec = _function_registry.load_function_module(_source)
        spec.loader.exec_module(source_module)

        self.user_function = _function_registry.get_user_function(_source, source_module, _target)

    def invoke_user_function(self, request):
        self.request = request
        if self.user_function:
            output_data = self.user_function(self)
            return output_data
        else:
            raise ValueError("User function is not loaded.")

    def run(self):
        runtime_context = RuntimeContext()
        runtime_context.context = self.context

        if runtime_context.has_dapr_trigger():
            _triggers = runtime_context.get_dapr_triggers()
            dapr_trigger = DaprTrigger(self.context.port, self.app, _triggers, self.user_function)
            dapr_trigger.start(runtime_context)

        self.app.run(50055)
