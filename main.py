from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from agent_framework import (
    Agent,
    AgentResponse,
    AgentSession,
    CompactionProvider,
    CompactionStrategy,
    InMemoryHistoryProvider,
    Message,
    SlidingWindowStrategy,
    SummarizationStrategy,
    TruncationStrategy,
    included_messages,
)
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

DEFAULT_STRATEGY = "summarization"


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


def build_strategy(name: str) -> CompactionStrategy:
    if name == "truncation":
        return TruncationStrategy(max_n=18, compact_to=10)

    if name == "sliding-window":
        return SlidingWindowStrategy(keep_last_groups=6)

    if name == "summarization":
        return SummarizationStrategy(
            client=github_client(),
            target_count=8,
            threshold=2,
            prompt="Summarize the user's preferences, important facts, and unresolved threads only",
        )

    raise ValueError(f"Unknown compaction strategy: {name}")


def print_history_stats(session: AgentSession, history: InMemoryHistoryProvider) -> None:
    stored: list[Message] = session.state.get(history.source_id, {}).get("messages", [])
    included = included_messages(stored)

    print(f"History snapshot: stored={len(stored)} | included={len(included)}")


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
    history = InMemoryHistoryProvider(skip_excluded=True)
    compaction = CompactionProvider(
        after_strategy=build_strategy(DEFAULT_STRATEGY), history_source_id=history.source_id
    )

    agent = Agent(
        client=github_client(),
        name="CompactingAgent",
        instructions=(
            "You are a witty assistant. "
            "Remember the user's preferences when enough history is still available."
        ),
        context_providers=[history, compaction],
    )
    session = agent.create_session()

    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input == "/quit":
            break

        if user_input == "/history":
            print_history_stats(session, history)
            print()
            continue

        response = await agent.run(user_input, session=session)
        print(f"Assistant: {response.text}")
        print(usage_summary(response))
        print_history_stats(session, history)
        print()


def main():
    load_dotenv()
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
