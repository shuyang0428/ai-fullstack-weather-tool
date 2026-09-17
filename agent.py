"""Command-line Anthropic weather agent. Configure it with .env."""

import json
import os

from anthropic import Anthropic

from weather import get_weather


weather_tool = {
    "name": "get_weather",
    "description": (
        "Use this when the user asks for a city's forecast, temperature, precipitation, "
        "weather conditions, or whether to bring an umbrella. The day accepts only today, "
        "tomorrow, or day_after_tomorrow, and defaults to today. For multiple cities, call "
        "this tool separately for each city; calls may be made simultaneously."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name to look up."},
            "day": {
                "type": "string",
                "enum": ["today", "tomorrow", "day_after_tomorrow"],
                "default": "today",
                "description": "Forecast day; defaults to today.",
            },
        },
        "required": ["city"],
    },
}


def load_dotenv(path=".env"):
    """Load simple KEY=VALUE pairs without another dependency."""
    try:
        with open(path, encoding="utf-8") as file:
            for line in file:
                key, sep, value = line.strip().partition("=")
                if sep and key and not key.startswith("#"):
                    os.environ.setdefault(key, value.strip().strip('"').strip("'"))
    except FileNotFoundError:
        pass


def run_agent():
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY in .env")
    client = Anthropic(api_key=api_key)
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "1024"))
    messages = []

    print("Weather agent. Type 'exit' to quit.")
    while (prompt := input("> ").strip()) not in {"exit", "quit"}:
        if not prompt:
            continue
        messages.append({"role": "user", "content": prompt})
        while True:
            response = client.messages.create(
                model=model, max_tokens=max_tokens, messages=messages, tools=[weather_tool]
            )
            messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason == "end_turn":
                print("".join(block.text for block in response.content if block.type == "text"))
                break
            tool_results = [
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(get_weather(**block.input), ensure_ascii=False),
                }
                for block in response.content if block.type == "tool_use"
            ]
            if not tool_results:
                print(f"Stopped unexpectedly: {response.stop_reason}")
                break
            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    run_agent()
