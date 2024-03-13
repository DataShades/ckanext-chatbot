from __future__ import annotations

import logging
import os

import requests
from openai import OpenAI
from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.chatbot import utils


log = logging.getLogger(__name__)
bp = Blueprint("chatbot", __name__)
bp.before_request(utils.before_request)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class ChatBotTalkView(MethodView):

    def get(self) -> str:
        return tk.render(
            "chatbot/talk.html",
            extra_vars={"chats": utils.get_user_chats(tk.current_user.id)},  # type: ignore
        )

    def post(self) -> str:
        prompt = tk.request.form["prompt"]

        if prompt:
            response = self.generate_response(prompt)
        else:
            response = "Please, provide a prompt"

        return response

    def generate_response(self, prompt: str) -> str:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Marv is a CKAN AI assistant bot and he answers only questions related to CKAN platform",
                },
                {
                    "role": "system",
                    "content": "When someone asks Marv about questions not related to CKAN, he says that he can help only with CKAN",
                },
                {
                    "role": "system",
                    "content": "Marv understands, that he's a CKAN AI assistant and he is on a CKAN portal",
                },
                {
                    "role": "system",
                    "content": "Marv understands, that user that asks a question is logged in to a CKAN portal and doesn't suggest them to log in",
                },
                {
                    "role": "system",
                    "content": "Marv returns a response in markdown format",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model="ft:gpt-3.5-turbo-0125:personal::91xHVRq2",
            # max_tokens=100,
            n=1,
        )

        return response.choices[0].message.content or ""


class ChatBotChatView(MethodView):
    def get(self, chat_id: str) -> str:
        return tk.render(
            "chatbot/talk.html",
            extra_vars={
                "chats": utils.get_user_chats(tk.current_user.id),  # type: ignore
                "active_chat": utils.get_chat(tk.current_user.id, chat_id),  # type: ignore
            },
        )


bp.add_url_rule("/chatbot/talk", view_func=ChatBotTalkView.as_view("talk"))
bp.add_url_rule("/chatbot/talk/<chat_id>", view_func=ChatBotChatView.as_view("chat"))
