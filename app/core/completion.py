from __future__ import annotations

import os

from openai import OpenAI
from pydantic import BaseModel

from app._enums import Models
from app.models.models import Completion
from app.utils.decorators import retry

__all__ = ["CompletionModel"]


class CompletionModel:
    """CompletionModel is a base class for generating completions using OpenAI's API."""

    def __init__(
        self,
        token: str | None = None,
        model_name: Models = Models.GPT_4_TURBO,
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
        model_name: Models = Models.GPT_4_TURBO,
        system_instruction: str | None = None,
        thinking_budget: int | None = None,
        reasoning_effort: str | None = None,
        images: list | None = None,
        response_format: type[BaseModel] | None = None,
    ) -> Completion | None:
        """
        Generates a completion using the specified model and prompt.

        Args:
            prompt (str): The input prompt for the model.
            model_name (Models): The model to use for generation.
            response_format (BaseModel | None): The format for the response.
            system_instruction (str | None): The system instruction to guide the model.
            thinking_budget (int | None): The budget for the model's thinking process.
            reasoning_effort (str | None): Reasoning effort for Gemini models.
            tools (list): Function calling tools.
            tool_choice (str | None): Tool choice for function calling.
            images (list): List of image dicts for multimodal input.

        Returns:
            Completion | None: The generated completion object.
        """
        pass
