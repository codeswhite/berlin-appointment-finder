import asyncio
import logging
from typing import List, Optional

import websockets
from dotenv import load_dotenv
from pydantic import BaseModel

from src.telegram import TelegramModule

load_dotenv()

WS_URL = "wss://allaboutberlin.com/api/appointments"


class AppointmentEvent(BaseModel):
    time: str
    status: int
    message: Optional[str]
    appointmentDates: List[str]
    lastAppointmentsFoundOn: str


class BurgeramtAppointmentFinder:
    logger = logging.getLogger(__name__)

    def __init__(self, telegram: TelegramModule):
        self.telegram = telegram
        self.logger.info("Initialized")

    async def listener_loop(self):
        self.logger.info("Starting listener loop...")
        try:
            while 1:
                try:
                    async with websockets.connect(WS_URL) as ws:
                        self.logger.info(f"Connected to {WS_URL}")
                        async for message in ws:
                            self.logger.debug(f"Received event: {message}")
                            try:
                                event = AppointmentEvent.parse_raw(message)
                                if event.status != 200:
                                    self.logger.error(
                                        f"Event status is not 200: {event.status}"
                                    )
                                    self.logger.error(f"Event message: {event.message}")
                                    continue
                            except Exception as e:
                                self.logger.error(f"Error parsing event: {e}")
                                continue
                            await self.telegram.new_appointments(event.appointmentDates)
                except Exception as e:
                    self.logger.error(
                        f"Connection closed, retrying in 5 sec.. Error was: {e}"
                    )
                    await asyncio.sleep(5)
        except asyncio.CancelledError:
            self.logger.info("WS Listener stopped")
