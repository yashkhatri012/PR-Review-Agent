import os
from dataclasses import dataclass
from groq import Groq
from dotenv import load_dotenv
from google import genai
from typing import TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)

load_dotenv()


@dataclass(frozen=True)
class ModelConfig:
    """Describe an LLM model available to the application.

    Attributes:
        name: Model identifier understood by the provider.
        provider: Provider responsible for serving the model.
        max_retries: Number of attempts allowed before falling back.
    """

    name: str
    provider: str
    max_retries: int = 1


class LLM:
    """Manage model selection and generation for the PR review system."""

    MODELS = (
        ModelConfig(
            name="gemini-2.5-flash",
            provider="gemini",
            max_retries=1,
        ),
        ModelConfig(
            name="openai/gpt-oss-20b",
            provider="groq",
            max_retries=1,
        ),
    )

    def __init__(self) -> None:
        """Initialize configured LLM clients and select the primary model."""
        self._clients = {}

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self._clients["gemini"] = genai.Client(
                api_key=gemini_api_key
            )

        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            self._clients["groq"] = Groq(
                api_key=groq_api_key
            )

        self._current_model = self._get_available_models()[0]
    def _get_available_models(self) -> list[ModelConfig]:
        """Return models whose providers have been configured.

        Returns:
            Configured models in fallback priority order.

        Raises:
            RuntimeError: If no configured LLM provider is available.
        """
        models = [
            model
            for model in self.MODELS
            if model.provider in self._clients
        ]

        if not models:
            raise RuntimeError(
                "No LLM providers are configured."
            )

        return models

    def _generate_gemini(
        self,
        model: ModelConfig,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """Generate structured output using Gemini.

        Args:
            model: Gemini model configuration.
            prompt: Prompt sent to Gemini.
            response_model: Expected Pydantic response model.

        Returns:
            Validated structured response.
        """
        client = self._clients["gemini"]

        response = client.models.generate_content(
            model=model.name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": response_model,
            },
        )

        return response_model.model_validate_json(response.text)

    def _generate_groq(
        self,
        model: ModelConfig,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """Generate structured output using Groq.

        Args:
            model: Groq model configuration.
            prompt: Prompt sent to Groq.
            response_model: Expected Pydantic response model.

        Returns:
            Validated structured response.
        """
        client = self._clients["groq"]

        response = client.chat.completions.create(
            model=model.name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": response_model.model_json_schema(),
                },
            },
        )

        content = response.choices[0].message.content

        return response_model.model_validate_json(content)
    @property
    def current_model(self) -> ModelConfig:
        """Return the model currently selected for generation.

        Returns:
            Configuration of the active LLM model.
        """
        return self._current_model

    def generate(self, prompt: str):
        """Generate a response from the currently selected LLM.

        Args:
            prompt: Prompt sent to the language model.

        Returns:
            The raw provider response.
        """
        model = self._current_model
        client = self._clients[model.provider]

        return client.models.generate_content(
            model=model.name,
            contents=prompt,
        )
    
    
    def _generate_with_model(
        self,
        model: ModelConfig,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """Generate structured output using the specified provider.

        Args:
            model: Model configuration determining the provider.
            prompt: Prompt sent to the model.
            response_model: Expected Pydantic response model.

        Returns:
            Validated structured response.

        Raises:
            ValueError: If the provider is unsupported.
        """
        if model.provider == "gemini":
            return self._generate_gemini(
                model,
                prompt,
                response_model,
            )

        if model.provider == "groq":
            return self._generate_groq(
                model,
                prompt,
                response_model,
            )

        raise ValueError(
            f"Unsupported LLM provider: {model.provider}"
        )
    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """Generate structured output with retries and provider fallback.

        Args:
            prompt: Prompt sent to the language model.
            response_model: Expected Pydantic response model.

        Returns:
            Validated response from the first successful provider.

        Raises:
            RuntimeError: If all configured providers fail.
        """
        errors: list[str] = []

        for model in self._get_available_models():

            for attempt in range(model.max_retries + 1):

                try:
                    self._current_model = model

                    return self._generate_with_model(
                        model=model,
                        prompt=prompt,
                        response_model=response_model,
                    )

                except Exception as exc:
                    errors.append(
                        f"{model.provider}/{model.name} "
                        f"attempt {attempt + 1}: {exc}"
                    )

        raise RuntimeError(
            "All configured LLM providers failed:\n"
            + "\n".join(errors)
        )