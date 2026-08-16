from abc import ABC, abstractmethod
from typing import Any
from services.llm import LLM
class BaseAgent(ABC):
    """Define the common interface and dependencies for review agents."""

    def __init__(self, llm: LLM) -> None:
        """Initialize an agent with an LLM service.

        Args:
            llm: Shared LLM service used to generate model responses.
        """
        self.llm = llm

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name identifying the agent.

        Returns:
            The agent's unique identifier.
        """
        ...

    @abstractmethod
    def review(self, **inputs: Any) -> Any:
        """Execute the agent's specialized review task.

        Args:
            **inputs: Inputs required by the specific agent.

        Returns:
            The structured result produced by the agent.
        """
        ...