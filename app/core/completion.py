from __future__ import annotations

import json
import os

from openai import OpenAI
from pydantic import BaseModel

from app._enums import Models
from app.models.models import Completion
from app.utils.decorators import retry
from app.utils.logger import logger

__all__ = ["CompletionModel"]


class CompletionModel:
    """CompletionModel is a base class for generating completions using OpenAI's API."""

    def __init__(
        self,
        token: str | None = None,
        model_name: Models = Models.GPT_4_1_MINI,
        temperature: float = 0,
        base_url: str | None = None,
        system_instruction: str = "You are a helpful assistant.",
        response_schema: dict | None = None,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.system_instruction = system_instruction
        self.response_schema = response_schema

        self.api_key = token or os.getenv("OPENAI_API_KEY")

        self.client = OpenAI(api_key=self.api_key)

    @retry(max_retries=3, sleep_time=3)
    def generate(
        self,
        prompt: str,
        model_name: Models = Models.GPT_4_1_MINI,
        system_instruction: str | None = None,
        thinking_budget: int | None = None,
        reasoning_effort: str | None = None,
        images: list | None = None,
        response_format: type[BaseModel] | None = None,
        tools: list | None = None,
    ) -> Completion | None:
        """Generate a completion using OpenAI's chat API."""
        messages: list[dict] = [
            {"role": "system", "content": system_instruction or self.system_instruction}
        ]

        if images:
            user_content: list[dict] = []
            if prompt:
                user_content.append({"type": "text", "text": prompt})

            for img in images:
                user_content.append({"type": "image_url", "image_url": {"url": img}})
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": prompt})

        params = {
            "model": model_name.value,
            "messages": messages,
            "temperature": self.temperature,
        }

        if response_format is not None:
            params["response_format"] = {"type": "json_object"}

        if tools is not None:
            params["tools"] = tools

        try:
            response = self.client.chat.completions.create(**params)

            # Handle tool calls if present
            if response.choices[0].message.tool_calls:
                tool_calls_data = []
                for tool_call in response.choices[0].message.tool_calls:
                    tool_call_info = {
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments),
                        },
                    }
                    tool_calls_data.append(tool_call_info)

                return Completion(
                    data={
                        "tool_calls": tool_calls_data,
                        "content": response.choices[0].message.content,
                    }
                )

            # Handle regular content response
            content: str = response.choices[0].message.content or ""

            if response_format is not None and content:
                parsed = response_format.model_validate_json(content)
                return Completion(data=parsed.model_dump())

            return Completion(data=content)

        except Exception as e:
            logger.error(
                f"Error generating completion: {e}",
                exc_info=True,
            )
            return Completion(data="")
