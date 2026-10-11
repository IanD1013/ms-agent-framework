from __future__ import annotations

import asyncio
import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

DEFAULT_OLLAMA_MODELS_ENDPOINT = "http://localhost:11434/v1/"
DEFAULT_OLLAMA_MODEL = "ministral-3"

DEFAULT_FOUNDRY_ENDPOINT = "https://nicovermeir-4297-resource.services.ai.azure.com"
DEFAULT_FOUNDRY_MODEL = "gpt-5.4-nano"

DEFAULT_GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference"
DEFAULT_GITHUB_MODELS_MODEL = "openai/gpt-4o-mini"
DEFAULT_PROMPT = "Tell me a joke about a pirate."


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Environment variable {name} is required.")
    return value


def github_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=DEFAULT_GITHUB_MODELS_MODEL,
        api_key=require_env("GITHUB_TOKEN"),
        base_url=DEFAULT_GITHUB_MODELS_ENDPOINT,
    )


def foundry_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=DEFAULT_FOUNDRY_MODEL,
        azure_endpoint=DEFAULT_FOUNDRY_ENDPOINT,
        credential=AzureCliCredential(),
    )


def ollama_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=DEFAULT_OLLAMA_MODEL,
        api_key="ollama",
        base_url=DEFAULT_OLLAMA_MODELS_ENDPOINT,
    )


def build_joker_agent() -> Agent:
    return Agent(
        client=github_client(),
        name="Joker",
        instructions=(
            "You are good at telling jokes. You always respond in the style of Shakespeare."
        ),
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
