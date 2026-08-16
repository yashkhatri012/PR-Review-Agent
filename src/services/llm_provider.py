import os
from typing import TypeVar

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class LLMProvider:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str, response_model: type[T]) -> T:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )

        if response.parsed is None:
            raise RuntimeError("LLM returned no structured response")

        return response.parsed

    import os
from typing import TypeVar

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class LLMProvider:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str, response_model: type[T]) -> T:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_model,
            ),
        )

        if response.parsed is None:
            raise RuntimeError("LLM returned no structured response")

        return response.parsed

    def generate_with_tools(
        self,
        contents: list,
        tools: list[dict],
    ):
        tool = types.Tool(
            function_declarations=tools,
        )

        config = types.GenerateContentConfig(
            tools=[tool],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )

        return self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )
    def continue_with_tool_result(
        self,
        contents: list,
        tool_name: str,
        tool_result: object,
    ):
        """Continue an LLM interaction after executing a requested tool.

        Args:
            contents: Conversation history containing the original request and
            the model's previous response.
            tool_name: Name of the tool that was executed.
            tool_result: Result returned by the executed tool.
        """
        tool_response = types.Part.from_function_response(
            name=tool_name,
            response={"result": tool_result},
        )

        contents.append(
            types.Content(
                role="tool",
                parts=[tool_response],
            )
        )

        return self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )