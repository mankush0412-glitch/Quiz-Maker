import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from quiz_parser import parse_quiz_file

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

QUIZ_DELAY_SECONDS = 0.5

user_states = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📺 Watch Tutorial", callback_data="tutorial"),
            InlineKeyboardButton("💎 Premium Plans", callback_data="premium"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⭐ Welcome to Quiz Bot! ⭐\n\n"
        "I can turn your text files into interactive 10-second quizzes!\n\n"
        "💠 Use /createquiz - Start quiz creation\n"
        "💠 Use /help - Show formatting guide\n"
        "💠 Use /token - Get your access token\n"
        "💠 Premium users get unlimited access!\n\n"
        "Let's make learning fun!",
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Quiz File Formatting Guide*\n\n"
        "Each question block must follow this format:\n\n"
        "```\n"
        "Question text here?\n"
        "A) Option one\n"
        "B) Option two\n"
        "C) Option three\n"
        "D) Option four\n"
        "Answer: B\n"
        "Solution: This is why B is correct.\n"
        "```\n\n"
        "*Rules:*\n"
        "• Options labeled A), B), C), D) etc.\n"
        "• `Answer:` line must have the correct letter\n"
        "• `Solution:` is optional — shown after user answers\n"
        "• Separate each question with a blank line\n"
        "• Max 14 questions per file\n"
        "• Options have NO serial numbers — just text\n\n"
        "*Example:*\n"
        "```\n"
        "Income from house property is chargeable under:\n"
        "A) Section 14\n"
        "B) Section 22\n"
        "C) Section 23\n"
        "D) Section 24\n"
        "Answer: B\n"
        "Solution: Section 22 deals with income from house property.\n"
        "```\n\n"
        "Use /createquiz to get started!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def token_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"🔑 Your Access Token:\n\n`USER_{user_id}`\n\n"
        "Keep this token safe. Use it to access premium features.",
        parse_mode="Markdown",
    )


async def createquiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = "waiting_for_file"
    await update.message.reply_text(
        "📋 Ready to create your quiz!\n\n"
        "Please send me a .txt file containing your questions.\n\n"
        "Need format help? Use /help"
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_states.get(user_id) != "waiting_for_file":
        await update.message.reply_text(
            "Please use /createquiz first to start quiz creation."
        )
        return

    document = update.message.document
    if not document.file_name.lower().endswith(".txt"):
        await update.message.reply_text("❌ Please send a .txt file only.")
        return

    await update.message.reply_text("⏳ Processing your file...")

    try:
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()
        content = file_bytes.decode("utf-8", errors="ignore")

        questions, errors = parse_quiz_file(content)

        if errors:
            error_text = f"⚠️ Found {len(errors)} error(s):\n\n"
            for err in errors[:5]:
                error_text += f"❌ {err}\n"
            if len(errors) > 5:
                error_text += f"\n...and {len(errors) - 5} more errors"
            if not questions:
                error_text += "\n\n❌ No valid questions found in file"
                await update.message.reply_text(error_text)
                user_states[user_id] = None
                return
            else:
                await update.message.reply_text(error_text)

        if not questions:
            await update.message.reply_text("❌ No valid questions found in file")
            user_states[user_id] = None
            return

        total = len(questions)

        await update.message.reply_text(
            f"✅ Successfully sent {total} quiz questions!"
        )

        user_states[user_id] = None

        for q in questions:
            try:
                explanation = q.get("solution") or None

                await context.bot.send_poll(
                    chat_id=update.effective_chat.id,
                    question=q["question"],
                    options=q["options"],
                    type="quiz",
                    correct_option_id=q["correct_index"],
                    is_anonymous=True,
                    open_period=10,
                    explanation=explanation,
                )
                await asyncio.sleep(QUIZ_DELAY_SECONDS)
            except Exception as e:
                logger.error(f"Error sending poll: {e}")

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await update.message.reply_text(
            "❌ Error processing your file. Please check the format and try again.\n"
            "Use /help to see the correct format."
        )
        user_states[user_id] = None


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "tutorial":
        await query.message.reply_text(
            "📺 *Tutorial*\n\n"
            "1. Use /createquiz to start\n"
            "2. Send your .txt file with questions\n"
            "3. Bot sends quiz polls with solutions automatically!\n\n"
            "Use /help to see the file format.",
            parse_mode="Markdown",
        )
    elif query.data == "premium":
        await query.message.reply_text(
            "💎 *Premium Plans*\n\n"
            "• Free: Up to 14 questions per quiz\n"
            "• Premium: Unlimited questions, priority support\n\n"
            "Contact admin for premium access.",
            parse_mode="Markdown",
        )


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required!")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("token", token_command))
    app.add_handler(CommandHandler("createquiz", createquiz_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("Quiz Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError("Loop is closed")
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    main()
