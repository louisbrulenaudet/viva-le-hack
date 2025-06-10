"""Utilities for generating Markdown reports from JSON analysis results."""

from __future__ import annotations

import json
from pathlib import Path

import openai


def generate_markdown_document(json_path: str) -> str:
    """Generate a technical Markdown report from an analysis JSON file."""

    data = json.loads(Path(json_path).read_text())
    title = str(data.get("title", "Analysis Report"))

    prompt_text = (
        "**Role:** You are a meticulous technical writer tasked with creating a comprehensive report.\n"
        "**Objective:** Summarize the analytical results provided in JSON format into a clear, well-structured Markdown document.\n"
        "**Output requirements:** Return only the Markdown text without code fences or extra commentary.\n\n"
        "**Formatting guidelines:**\n"
        "1. Start with a '# ' heading using the 'title' value.\n"
        "2. Present key findings in distinct '## ' sections.\n"
        "3. Use lists or tables when beneficial.\n"
        "4. Keep the language concise and technical.\n"
        "5. Do not mention the JSON input or these instructions."
    )

    user_payload = {"title": title, "results": data.get("results", data)}

    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": json.dumps(user_payload)},
    ]

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=1500,
        temperature=0.2,
    )

    markdown = response.choices[0].message.content.strip()

    if markdown.startswith("```"):
        markdown = markdown.strip("`\n ")

    return markdown
