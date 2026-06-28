from html import escape
from typing import (
    Any,
    ClassVar,
    MutableMapping,
    Optional,
)

from pyrogram.client import Client
from pyrogram.errors import (
    ChannelPrivate,
MessageDeleteForbidden,
    ChatWriteForbidden,
)
from pyrogram.types import Chat, Message, User

from anjani import plugin, util

class Greeting(plugin.Plugin):
    name: ClassVar[str] = "Greetings"
    helpable: ClassVar[bool] = True

    chat_db: util.db.AsyncCollection

    async def on_load(self) -> None:
        self.chat_db = self.bot.db.get_collection("CHATS")


    async def on_chat_action(self, message: Message) -> None:
    chat = message.chat
    reply_to = message.id

    if message.left_chat_member and message.left_chat_member.id == self.bot.uid:
        return

    thread_id = await self.get_action_topic(chat)

    if message.left_chat_member:
        await self._member_leave(message, reply_to, thread_id)
        
    async def _member_leave(
    self, message: Message, reply_to: int, thread_id: Optional[int]
) -> None:
    chat = message.chat
    left_member = message.left_chat_member

    text = "👋 {mention} left the chat."

    formatted_text = await self._build_text(
        text, left_member, chat, self.bot.client
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

    @staticmethod
    async def _build_text(
        text: str, user: User, chat: Chat, client: Optional[Client] = None
    ) -> str:
        first_name = user.first_name or ""  # Ensure first name is not None
        last_name = user.last_name
        full_name = first_name + last_name if last_name else first_name
        try:
            count = await client.get_chat_members_count(chat.id) if client else "N/A"
        except ChannelPrivate:
            count = "N/A"

        username = util.tg.get_username(user)

        return text.format(
            first=escape(first_name),
            last=escape(last_name) if last_name else "",
            fullname=escape(full_name),
            username=f"@{username}" if username else user.mention,
            mention=user.mention,
            count=count,
            chatname=escape(chat.title),
            id=user.id,
        )

    async def get_action_topic(self, chat: Chat) -> Optional[int]:
        if not chat.is_forum:
            return None
        data = await self.chat_db.find_one({"chat_id": chat.id}, {"action_topic": True})
        return data.get("action_topic") if data else None
