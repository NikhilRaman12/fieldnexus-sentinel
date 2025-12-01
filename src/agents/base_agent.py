from abc import ABC, abstractmethod
import pandas as pd

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
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Each agent must implement its own logic here.
        """
        pass

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standard wrapper for agent execution.
        Ensures uniform behavior across all agents.
        """
        if df is None:
            raise ValueError(f"{self.name}: Input DataFrame cannot be None")

        result = self.execute(df)

        if not isinstance(result, pd.DataFrame):
            raise TypeError(
                f"{self.name}: execute() must return a pandas DataFrame"
            )

        return result
