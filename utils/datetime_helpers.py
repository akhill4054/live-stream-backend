from datetime import datetime, timezone


def get_utc_timestamp() -> int:
    now = datetime.now(timezone.utc)
    utc_time = now.replace(tzinfo=timezone.utc)
    return int(utc_time.timestamp())
