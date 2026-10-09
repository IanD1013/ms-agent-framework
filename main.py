from __future__ import annotations

import asyncio
import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient 
from dotenv import load_dotenv

DEFAULT_GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference"
DEFAULT_GITHUB_MODELS_MODEL = "openai/gpt-4o-mini"
DEFAULT_PROMPT = "Tell me a joke about a pirate."

def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Environment variable {name} is required.")
    return value

def github_models_client(*, model: str | None = None) -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=model or os.getenv("GITHUB_MODELS_MODEL") or DEFAULT_GITHUB_MODELS_MODEL,
        api_key=require_env("GITHUB_TOKEN"),
        base_url=os.getenv("GITHUB_MODELS_ENDPOINT") or DEFAULT_GITHUB_MODELS_ENDPOINT
    )

def build_joker_agent(*, model: str | None = None) -> Agent:
    return Agent(
        client=github_models_client(model=model),
        name="Joker",
        instructions="You are good at telling jokes. You always respond in the style of Shakespeare."
    )

async def async_main() -> None:
    joker = build_joker_agent()
    print(f"Sending prompt to {joker.name}: {DEFAULT_PROMPT}")
    response = await joker.run(DEFAULT_PROMPT)
    print(response.text)

def main():
    load_dotenv()
    asyncio.run(async_main())

if __name__ == "__main__":
    main()