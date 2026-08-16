from abc import ABC, abstractmethod
from typing import Any

from services.llm_provider import LLMProvider


class BaseAgent(ABC):
    """Define the common interface and dependencies for review agents.

    Each specialized review agent inherits from this class and implements
    its own domain-specific review behavior while sharing the same LLM
    provider interface.
    """

    def __init__(self, llm: LLMProvider) -> None:
        """Initialize an agent with an LLM provider.

        Args:
            llm: Provider used by the agent to communicate with the language
                model.
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