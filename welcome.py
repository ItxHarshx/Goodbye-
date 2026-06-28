from html import escape
from typing import ClassVar, Optional

from pyrogram.errors import ChatWriteForbidden
from pyrogram.types import Chat, Message, User

from anjani import plugin


class Goodbye(plugin.Plugin):
    name: ClassVar[str] = "Goodbye"
    helpable: ClassVar[bool] = False

    async def on_chat_action(self, message: Message) -> None:
        chat = message.chat

        if not message.left_chat_member:
            return

        # ignore bot itself
        if message.left_chat_member.id == self.bot.uid:
            return

        await self._member_leave(message)

    async def _member_leave(self, message: Message) -> None:
        chat = message.chat
        user = message.left_chat_member

        text = "👋 {mention} left the chat."

        formatted_text = text.format(
            mention=user.mention,
            first=escape(user.first_name or ""),
            id=user.id,
        )

        try:
            await self.bot.client.send_message(
                chat.id,
                formatted_text,
                reply_to_message_id=message.id,
            )
        except ChatWriteForbidden:
            return
