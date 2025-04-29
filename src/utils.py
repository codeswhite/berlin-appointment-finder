import datetime
from typing import Optional


def strip_date(date_str: str) -> str:
    return date_str.split("T")[0]


def format_date(date: datetime.datetime) -> str:
    return date.strftime("%Y-%m-%d")


def parse_date(date_str: Optional[str]) -> Optional[datetime.datetime]:
    if not date_str or not strip_date(date_str):
        return None
    try:
        return datetime.datetime.fromisoformat(strip_date(date_str))
    except ValueError:
        raise ValueError(
            f"Error while parsing date format: {date_str}, should be: YYYY-MM-DD"
        )


def is_within_dates(
    date: datetime.datetime,
    from_date: Optional[datetime.datetime],
    to_date: Optional[datetime.datetime],
) -> bool:
    if from_date and date < from_date:
        return False
    if to_date and date > to_date:
        return False
    return True


# A link showing specifically month May of 2025 (timestamp is: May 30, 2025)
# BOOKING_PAGE_MAY = "https://service.berlin.de/terminvereinbarung/termin/day/1748642400/"
BOOKING_PAGE = "https://service.berlin.de/terminvereinbarung/termin/all/120686/"
