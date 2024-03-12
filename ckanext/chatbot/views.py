from __future__ import annotations

import logging

import os

from openai import OpenAI
from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk


log = logging.getLogger(__name__)
bp = Blueprint("chatbot", __name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class ChatBotTalkView(MethodView):

    def get(self) -> str:
        return tk.render("chatbot/talk.html", extra_vars={"data": {}, "errors": {}})

    def post(self) -> str:
        promt = tk.request.form["promt"]

        if promt:
            response = self.generate_response(promt)
        else:
            response = "Please, provide a promt"

        print(response)

        return response

    def generate_response(self, prompt: str) -> str:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Marv is a factual chatbot that is also sarcastic",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model="ft:gpt-3.5-turbo-0125:personal::91xHVRq2",
            max_tokens=100,
            n=1,
        )

        return response.choices[0].message.content or ""


bp.add_url_rule("/chatbot/talk", view_func=ChatBotTalkView.as_view("talk"))
