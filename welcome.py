from html import escape
from typing import ClassVar, Optional

from pyrogram.client import Client
from pyrogram.errors import (
    ChannelPrivate,
    ChatWriteForbidden,
)
from pyrogram.types import Chat, Message, User

from anjani import plugin, command, filters, util


class Greeting(plugin.Plugin):
    name: ClassVar[str] = "Goodbye"
    helpable: ClassVar[bool] = True

    chat_db: util.db.AsyncCollection

    async def on_load(self) -> None:
        self.chat_db = self.bot.db.get_collection("CHATS")

    # -------------------------
    # EVENT: user left chat
    # -------------------------
    async def on_chat_action(self, message: Message) -> None:
        chat = message.chat
        reply_to = message.id

        # Ignore bot itself leaving
        if message.left_chat_member and message.left_chat_member.id == self.bot.uid:
            return

        # Optional clean service message
        if await self.clean_service(chat.id):
            try:
                await message.delete()
            except Exception:
                pass
            reply_to = 0

        thread_id = await self.get_action_topic(chat)

        if message.left_chat_member:
            await self._member_leave(message, reply_to, thread_id)

    # -------------------------
    # HANDLE LEAVE MESSAGE
    # -------------------------
    async def _member_leave(
        self,
        message: Message,
        reply_to: int,
        thread_id: Optional[int],
    ) -> None:
        chat = message.chat
        user = message.left_chat_member

        text = "👋 {mention} left the chat."

        formatted_text = await self._build_text(
            text, user, chat, self.bot.client
        )

        try:
            await self.bot.client.send_message(
                chat.id,
                formatted_text,
                reply_to_message_id=reply_to if not thread_id else None,
                message_thread_id=thread_id,
            )
        except ChatWriteForbidden:
            return

    # -------------------------
    # TEXT FORMATTER
    # -------------------------
    @staticmethod
    async def _build_text(
        text: str,
        user: User,
        chat: Chat,
        client: Optional[Client] = None,
    ) -> str:
        return text.format(
            mention=user.mention,
            first=escape(user.first_name or ""),
            id=user.id,
        )

    # -------------------------
    # FOR FORUM THREAD SUPPORT
    # -------------------------
    async def get_action_topic(self, chat: Chat) -> Optional[int]:
        if not chat.is_forum:
            return None

        data = await self.chat_db.find_one(
            {"chat_id": chat.id},
            {"action_topic": True},
        )
        return data.get("action_topic") if data else None

    # -------------------------
    # CLEAN SERVICE MESSAGE (OPTIONAL)
    # -------------------------
    async def clean_service(self, chat_id: int) -> bool:
        clean = await self.chat_db.find_one(
            {"chat_id": chat_id},
            {"clean_service": 1},
        )
        return clean.get("clean_service", True) if clean else False
