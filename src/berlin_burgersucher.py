import asyncio
import os
import datetime
import time

import websockets
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List

from telegram import TelegramModule

load_dotenv()

WS_URL = "wss://allaboutberlin.com/api/appointments"

# A link showing specifically month May of 2025 (timestamp is: May 30, 2025)
# BOOKING_PAGE_MAY = "https://service.berlin.de/terminvereinbarung/termin/day/1748642400/"  

BOOKING_PAGE = "https://service.berlin.de/terminvereinbarung/termin/all/120686/"


class Utils:
    @staticmethod
    def strip_date(date_str: str) -> str:
        return date_str.split("T")[0]

    @staticmethod
    def format_date(date: datetime.datetime) -> str:
        return date.strftime("%Y-%m-%d")

    @staticmethod
    def parse_date_arg(date_str: Optional[str]) -> Optional[datetime.datetime]:
        if not date_str or not Utils.strip_date(date_str):
            return None
        try:
            return datetime.datetime.fromisoformat(Utils.strip_date(date_str))
        except Exception:
            print(f"Error while parsing date format: {date_str}, should be: YYYY-MM-DD")
            exit(1)

    @staticmethod
    def parse_dates_from_env() -> tuple[
        Optional[datetime.datetime], Optional[datetime.datetime]
    ]:
        appointment_since = Utils.parse_date_arg(os.getenv("APPOINTMENT_SINCE"))
        if appointment_since:
            print(f"APPOINTMENT_SINCE set to {appointment_since}")
        appointment_before = Utils.parse_date_arg(os.getenv("APPOINTMENT_BEFORE"))
        if appointment_before:
            print(f"APPOINTMENT_BEFORE set to {appointment_before}")
        if not appointment_since or not appointment_before:
            print(
                "WARNING: Both APPOINTMENT_BEFORE and APPOINTMENT_SINCE are missing, So you will be notified of all events!!"
            )
        return appointment_since, appointment_before


##
####
##


class AppointmentEvent(BaseModel):
    time: str
    status: int
    message: Optional[str]
    appointmentDates: List[str]
    lastAppointmentsFoundOn: str


class BurgeramtAppointmentSucher:
    def __init__(self):
        self.appointment_since, self.appointment_before = Utils.parse_dates_from_env()
        # Top N - Between 1 and 5
        self.send_top_n = max(1, min(5, int(os.getenv("SEND_TOP_N", 5))))
        self.telegram = TelegramModule()

        while 1:
            try:
                asyncio.run(self.listener_loop())
            except Exception as e:
                print(f"Error in listener loop: {e}")
                time.sleep(10)

    def is_within_configured_dates(
        self,
        date_str: str,
    ) -> bool:
        date = datetime.datetime.fromisoformat(Utils.strip_date(date_str))
        if self.appointment_before and date > self.appointment_before:
            return False
        if self.appointment_since and date < self.appointment_since:
            return False
        return True

    def compile_message_for_user(self, date_str: str) -> str:
        message_text = f"Appointment found on <b>{Utils.strip_date(date_str)}</b>.\n\nBook here: {BOOKING_PAGE}\n\n"
        if self.appointment_since:
            message_text += (
                f"\t(Its after: {Utils.format_date(self.appointment_since)})\n"
            )
        if self.appointment_before:
            message_text += (
                f"\t(Its before: {Utils.format_date(self.appointment_before)})\n"
            )
        return message_text

    async def listener_loop(self):
        async with websockets.connect(WS_URL) as ws:
            print(f"Connected to {WS_URL}")
            async for message in ws:
                print(f"Received event: {message}")
                try:
                    event = AppointmentEvent.parse_raw(message)
                except Exception as e:
                    print(f"Error parsing event: {e}")
                    continue

                # Check for appointments before configured date
                matching_dates = [
                    date
                    for date in event.appointmentDates[: self.send_top_n]
                    if self.is_within_configured_dates(date)
                ]
                for date in matching_dates:
                    print(f"Appointment found on {date}, sending message...")
                    await self.telegram.send_telegram_message(
                        self.compile_message_for_user(date),
                    )


if __name__ == "__main__":
    try:
        BurgeramtAppointmentSucher()
    except KeyboardInterrupt:
        print("Stopped.")
