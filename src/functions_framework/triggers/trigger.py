from abc import ABC, abstractmethod

from functions_framework.context.runtime_context import RuntimeContext


class TriggerHandler(ABC):
    @abstractmethod
    def start(self, context: RuntimeContext):
        pass

