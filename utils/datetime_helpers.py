from datetime import datetime, timezone


def get_utc_timestamp():
    now = datetime.now(timezone.utc)
    utc_time = now.replace(tzinfo=timezone.utc)
    return utc_time.timestamp()
