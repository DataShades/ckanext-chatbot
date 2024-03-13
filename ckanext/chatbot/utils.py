from __future__ import annotations

import uuid
from typing import Any, cast

import ckan.types as types
import ckan.plugins.toolkit as tk

import ckanext.chatbot.const as const
from ckanext.chatbot import const, types as cb_types


def create_chat(user_id: str) -> cb_types.Chat:
    flake = get_data_from_flake(const.FLAKE_CHATS.format(user_id))

    new_chat = cb_types.Chat(chat_id=str(uuid.uuid4()), messages=[])

    flake["data"].setdefault("chats", {})
    flake["data"]["chats"][new_chat["chat_id"]] = new_chat

    store_data_in_flake(const.FLAKE_CHATS.format(user_id), flake["data"])

    return new_chat


def get_chat(user_id: str, chat_id: str) -> cb_types.Chat | None:
    flake = get_data_from_flake(const.FLAKE_CHATS.format(user_id))

    for chat in flake["data"]["chats"]:
        if chat["chat_id"] == chat_id:
            return chat

    return None


def get_user_chats(user_id: str) -> list[cb_types.Chat]:
    flake = get_data_from_flake(const.FLAKE_CHATS.format(user_id))

    if "chats" not in flake["data"]:
        return [create_chat(user_id)]

    return list(flake["data"]["chats"].values())


def drop_chat(user_id: str, chat_id: str) -> bool:
    flake = tk.get_action("flakes_flake_lookup")(
        prepare_context(),
        {"name": const.FLAKE_CHATS.format(user_id), "author_id": None},
    )

    chat = flake["data"]["chats"].pop(chat_id, None)

    return bool(chat)


def add_message_to_chat(message: cb_types.Message, chat_id: str) -> None:
    pass


def prepare_context() -> types.Context:
    return cast(
        types.Context,
        {"ignore_auth": True},
    )


def store_data_in_flake(flake_name: str, data: Any) -> dict[str, Any]:
    """Save the serializable data into the flakes table."""
    return tk.get_action("flakes_flake_override")(
        prepare_context(),
        {"author_id": None, "name": flake_name, "data": data},
    )


def get_data_from_flake(flake_name: str) -> dict[str, Any]:
    """Retrieve a previously stored data from the flake."""
    try:
        return tk.get_action("flakes_flake_lookup")(
            prepare_context(),
            {"author_id": None, "name": flake_name},
        )
    except tk.ObjectNotFound:
        return tk.get_action("flakes_flake_create")(
            prepare_context(),
            {"author_id": None, "name": flake_name, "data": {}},
        )


def before_request() -> None:
    if tk.current_user.is_anonymous:
        tk.abort(403, tk._("You have to be authorized"))
