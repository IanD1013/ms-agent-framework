from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from agent_framework import Agent, AgentResponse, AgentSession
from agent_framework.devui import serve
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

FILE_SESSION_PATH = "session.json"


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
        instructions=("You are good at telling jokes."),
    )


def build_translator_agent() -> Agent:
    return Agent(
        client=github_client(),
        name="Translator",
        instructions="You are a helpful translator. Translate every answer into French.",
    )


def build_entities() -> list[Agent]:
    return [build_joker_agent(), build_translator_agent()]


def usage_summary(response: AgentResponse) -> str:
    usage = response.usage_details
    if usage is None:
        return "Usage summary: unavailable"

    input_tokens = usage.get("input_token_count")
    output_tokens = usage.get("output_token_count")
    total_tokens = usage.get("total_token_count")

    return f"Usage summary: input={input_tokens}, output={output_tokens}, total={total_tokens}"


def save_session(path: Path, session: AgentSession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")


def load_session(path: Path) -> AgentSession | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return AgentSession.from_dict(data)


PROMPTS = (
    "Tell me 3 jokes about celebrities.",
    "List the celebrities you used in those jokes.",
    "Tell me 3 jokes about pirates.",
)


async def async_main() -> None:
    joker = build_joker_agent()
    path = Path(FILE_SESSION_PATH)
    session: AgentSession | None = load_session(path)

    if session is None:
        session = joker.create_session()
        print(f"Created new local session: {session.session_id}")
    else:
        print(f"Loaded local session: {session.session_id}")

    for prompt in PROMPTS:
        response = await joker.run(prompt, session=session)
        save_session(path, session)
        print(f"You: {prompt}")
        print(f"Joker: {response.text}")
        print(usage_summary(response))
        print()


def main():
    load_dotenv()
    asyncio.run(async_main())
    serve(entities=build_entities(), auth_enabled=False, auto_open=True)


if __name__ == "__main__":
    main()
