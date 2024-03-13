from __future__ import annotations

from typing import Literal, TypedDict


class Chat(TypedDict):
    chat_id: str
    messages: list[Message]


class Message(TypedDict):
    role: Literal["assistant"] | Literal["user"] | Literal["system"]
    content: str
