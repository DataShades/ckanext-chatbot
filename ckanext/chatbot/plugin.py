from __future__ import annotations

from typing import Any

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.chatbot.cli import register_commands


@toolkit.blanket.blueprints
class ChatbotPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IClick)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "chatbot")

    # IClick

    def get_commands(self) -> list[Any]:
        return register_commands()
