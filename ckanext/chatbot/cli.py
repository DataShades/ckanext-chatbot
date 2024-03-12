from __future__ import annotations

import os
import json
from collections import defaultdict

import click
from openai import OpenAI


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@click.group()
def chatbot():
    pass


@chatbot.command()
def tune():
    HERE = os.path.dirname(__file__)
    data_path = os.path.join(HERE, "data/test_fine_tuning.jsonl")

    with open(data_path, "r", encoding="utf-8") as file:
        dataset = [json.loads(line) for line in file]

    errors = validate_conversation(dataset)

    if errors:
        return click.secho(errors)

    tune_file = client.files.create(file=open(data_path, "rb"), purpose="fine-tune")
    client.fine_tuning.jobs.create(training_file=tune_file.id, model="gpt-3.5-turbo")


@chatbot.command()
def check_tune():
    """Check fine-tune jobs state"""
    result = client.fine_tuning.jobs.list()

    for job in result:
        color = "blue" if job.fine_tuned_model else "red"
        click.secho(
            f"JOB <ID={job.id}> <STATE={job.status}> <TUNED_MODEL={job.fine_tuned_model}",
            fg=color,
        )


def validate_conversation(
    dataset: list[dict[str, list[dict[str, str]]]]
) -> dict[str, int]:
    errors = defaultdict(int)

    for ex in dataset:
        if not isinstance(ex, dict):
            errors["data_type"] += 1
            continue

        messages = ex.get("messages", None)
        if not messages:
            errors["missing_messages_list"] += 1
            continue

        for message in messages:
            if "role" not in message or "content" not in message:
                errors["message_missing_key"] += 1

            if any(
                k not in ("role", "content", "name", "function_call", "weight")
                for k in message
            ):
                errors["message_unrecognized_key"] += 1

            if message.get("role", None) not in (
                "system",
                "user",
                "assistant",
                "function",
            ):
                errors["unrecognized_role"] += 1

            content = message.get("content", None)
            function_call = message.get("function_call", None)

            if (not content and not function_call) or not isinstance(content, str):
                errors["missing_content"] += 1

        if not any(message.get("role", None) == "assistant" for message in messages):
            errors["example_missing_assistant_message"] += 1

    return errors


def register_commands():
    return [chatbot]
