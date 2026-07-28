from abc import ABC, abstractmethod


class AICapability(ABC):
    """One subclass per AI capability. Keeps prompts colocated with the code that calls them."""

    @abstractmethod
    def run(self, *args, **kwargs):
        raise NotImplementedError
