from typing import Dict, Any
from abc import ABC, abstractmethod
from schemas import AgentScore

class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the agent"""
        pass

    @abstractmethod
    async def analyze(self, url: str) -> AgentScore:
        """
        Analyze the given URL and return a structured AgentScore.
        """
        pass
