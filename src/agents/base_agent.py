from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """
    BaseAgent defines the core interface that all agents must follow.
    Provides:
    - Standard run() method
    - Consistent input/output handling
    - Enforced implementation of execute()
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Each agent must implement its own logic here.
        """
        pass

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Standard wrapper for agent execution.
        Ensures uniform behavior across all agents.
        """
        return self.execute(*args, **kwargs)

