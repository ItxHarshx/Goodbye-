from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters


# -------------------------
# USER LEFT HANDLER
# -------------------------
async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message:
        return

    left_user = message.left_chat_member

    # ignore bot itself
    if not left_user or left_user.id == context.bot.id:
        return

    text = f"👋 {left_user.mention_html()} left the chat."

    await context.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        parse_mode="HTML",
        reply_to_message_id=message.message_id,
    )


# -------------------------
# HANDLER SETUP
# -------------------------
def setup(application):
    application.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye)
    )
