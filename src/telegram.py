import datetime
import os
import signal
import sys
from typing import List, Optional

from dotenv import load_dotenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PicklePersistence,
    filters,
)

from src import utils
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Set lower log level for httpx
logging.getLogger("httpx").setLevel(logging.WARNING)


# User states enum:
class UserState:
    ACTIVE = 1
    SETTING_RANGE = 2


# Buttons enum:
class ButtonsEnum:
    START_ALL_APPOINTMENTS = "start_all_appointments"
    START_SET_RANGE = "start_set_range"


class TelegramModule:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            self.logger.error("Telegram credentials (TELEGRAM_BOT_TOKEN) not set.")
            exit(1)

        self.burger_sucher_task = None
        self.app: Application = None
        self.appointment_dates: List[datetime.datetime] = []

    async def search_and_notify_user(self, user_id: int, user_data: dict) -> bool:
        if not user_id or not user_data:
            self.logger.error(f"Invalid user tuple: {user_id, user_data}")
            raise ValueError("DEV ERR: Invalid user tuple")
        if not user_data.get("state") == UserState.ACTIVE:
            self.logger.error("DEV ERR: User is not active")
            return False

        date_from: Optional[datetime.datetime] = user_data.get("date_from")
        date_to: Optional[datetime.datetime] = user_data.get("date_to")

        appointments_found = list(
            filter(
                lambda date: utils.is_within_dates(date, date_from, date_to),
                self.appointment_dates,
            )
        )

        if appointments_found:
            # Craft string
            text = f"Appointment{'s' if len(appointments_found) > 1 else ''} found:\n"
            for date in appointments_found:
                text += f"\n- *{utils.format_date(date)}*"

            self.logger.debug(
                f"Sending message to user {user_id}: '{text}'"
            )

            await self.app.bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="➡️ Book here ⬅️",
                                url=utils.BOOKING_PAGE,
                            )
                        ]
                    ]
                ),
            )

            self.logger.debug(
                f"Sent {len(appointments_found)} appointments to user {user_id}"
            )
        return bool(appointments_found)

    async def perform_bulk_search_and_notify(self, user_id: Optional[int] = None):
        all_user_data = await self.app.persistence.get_user_data()
        active_users = [
            (user_id, user_data)
            for user_id, user_data in all_user_data.items()
            if user_data.get("state") == UserState.ACTIVE
        ]
        for user_id, user_data in active_users:
            await self.search_and_notify_user(user_id, user_data)

    async def new_appointments(self, appointment_dates: List[str]):
        self.appointment_dates = list(map(utils.parse_date, appointment_dates))
        self.logger.info(
            f"New appointments batch: {list(map(utils.format_date, self.appointment_dates))}"
        )
        await self.perform_bulk_search_and_notify()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug(f"Start command received, user: {update.effective_user.id}")
        await update.message.reply_text(
            (
                "**👋 Welcome to the Berlin Burgeramt Appointment Finder Bot!**"
                "\n\nGet notified about:"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "All appointments",
                            callback_data=ButtonsEnum.START_ALL_APPOINTMENTS,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Set a date range",
                            callback_data=ButtonsEnum.START_SET_RANGE,
                        )
                    ],
                ]
            ),
        )

    async def query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == ButtonsEnum.START_ALL_APPOINTMENTS:
            context.user_data.update({"state": UserState.ACTIVE})
            await self.search_and_notify_user(
                update.effective_user.id, context.user_data
            )
            await query.edit_message_text(
                "You will be notified about all future appointment openings."
            )
            return

        elif query.data == ButtonsEnum.START_SET_RANGE:
            await query.edit_message_text(
                "**Acceptable formats are:**\n"
                "- `YYYY-MM-DD` -- A specific date\n"
                "- `YYYY-MM-DD to YYYY-MM-DD` -- A range\n"
                "- `YYYY-MM-DD to` -- Since specific date\n"
                "- `to YYYY-MM-DD` -- Until specific date\n",
                parse_mode="Markdown",
            )
            context.user_data.update({"state": UserState.SETTING_RANGE})
            return

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = (
            "**Usage:**\n"
            "/start - Show welcome and controls\n"
            "/stop - Stop receiving notifications\n"
            "/format - Show acceptable date formats\n"
            "/help - Show this help message\n\n"
            "Configure your desired appointment date range, then start receiving notifications.\n"
            "Use the buttons to control your preferences."
        )
        await update.message.reply_text(text, parse_mode="Markdown")

    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug(f"Text command received, user: {update.effective_user.id}")
        if context.user_data.get("state") == UserState.SETTING_RANGE:
            date_from = date_to = None
            if update.message and update.message.text:
                if "to" in update.message.text:
                    try:
                        # parse date range
                        _from, _, _to = update.message.text.partition("to")
                        if _from:
                            date_from = utils.parse_date(_from.strip())
                        if _to:
                            date_to = utils.parse_date(_to.strip())

                    except ValueError:
                        return await update.message.reply_text(
                            "Invalid format, try again"
                        )
                    except Exception:
                        return await update.message.reply_text(
                            "Sorry I have an error, try again"
                        )
                else:
                    try:
                        date = utils.parse_date(update.message.text)
                        if not date:
                            return await update.message.reply_text(
                                "Sorry I have an error, try again",
                            )
                        date_to = date_from = date
                    except ValueError:
                        return await update.message.reply_text(
                            "Invalid format, try again"
                        )
                    except Exception:
                        return await update.message.reply_text(
                            "Sorry I have an error, try again"
                        )

            # Store in user_data for persistence
            context.user_data["state"] = UserState.ACTIVE
            context.user_data["date_from"] = date_from
            context.user_data["date_to"] = date_to
            self.logger.debug(
                f"Applied settings, user: {update.effective_user.id}, settings: {context.user_data}"
            )

            # Run check immediately
            found_from_cache = await self.search_and_notify_user(
                update.effective_user.id, context.user_data
            )
            if not found_from_cache:
                await update.message.reply_text(
                    "Ok, I will let you know once I find an appointment for you."
                    "\nBe quick to book it before others!\n"
                    f"{date_from and f'\nFrom: {utils.format_date(date_from)}' or ''}"
                    f"{date_to and f'\nTo: {utils.format_date(date_to)}' or ''}"
                    "\n\nTo stop receiving notifications, send /stop."
                )

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.debug(f"Stop command received, user: {update.effective_user.id}")
        context.user_data.clear()
        await update.message.reply_text(
            ("I won't bother you anymore.\n\nTo start again, send /start.")
        )

    async def post_init(self, app: Application):
        # self.app = app
        # Import here to avoid circular import
        from src.berlin_burgersucher import BurgeramtAppointmentSucher

        self.burger_sucher_task = app.create_task(
            BurgeramtAppointmentSucher(self).listener_loop()
        )

    async def post_stop(self, app: Application):
        if self.burger_sucher_task:
            self.burger_sucher_task.cancel()
            await self.burger_sucher_task
            self.logger.info("Background task cancelled cleanly.")

    def run(self):
        self.logger.info("Starting Telegram bot...")
        persistence = PicklePersistence(filepath="bot_data.pkl")
        self.app = (
            Application.builder()
            .persistence(persistence)
            .token(self.bot_token)
            .post_init(self.post_init)
            .post_stop(self.post_stop)
            .build()
        )
        self.app.add_handler(CommandHandler("start", self.start_command))
        # self.app.add_handler(CommandHandler("format", self.help_format))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("usage", self.help_command))
        self.app.add_handler(CommandHandler("about", self.help_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CommandHandler("end", self.stop_command))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler)
        )
        self.app.add_handler(CallbackQueryHandler(self.query_handler))
        self.app.run_polling(
            allowed_updates=Update.ALL_TYPES,  # TODO restrict this?
            stop_signals={signal.SIGINT, signal.SIGTERM, signal.SIGABRT},
        )
        self.logger.info("Telegram bot stopped.")
