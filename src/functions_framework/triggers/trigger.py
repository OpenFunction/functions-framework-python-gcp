from abc import ABC, abstractmethod

from functions_framework.context.runtime_context import RuntimeContext


class Trigger(ABC):
    @abstractmethod
    def start(self, context: RuntimeContext):
        pass

