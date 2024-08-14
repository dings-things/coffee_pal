from datetime import datetime, timezone, timedelta


def convert_unix_to_kst(unix_timestamp: float) -> str:
    dt_utc = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    kst = timezone(timedelta(hours=9))
    dt_kst = dt_utc.astimezone(kst)
    return dt_kst.strftime("%Y년 %m월 %d일 %H시 %M분")


def now_kst() -> datetime:
    return datetime.now(timezone(timedelta(hours=9)))
