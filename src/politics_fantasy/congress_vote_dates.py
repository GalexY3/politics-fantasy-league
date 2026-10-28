"""Strict document-local Spanish vote date normalizer, never publication timestamp."""
import re
from datetime import date

def normalized_vote_date(value: str) -> str:
    if not isinstance(value,str) or not re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}",value):
        raise ValueError("VOTE_DATE_FORMAT")
    day,month,year=(int(v) for v in value.split("/"))
    try:
        if year<1977 or year>2100:raise ValueError("VOTE_YEAR_OUTSIDE_SUPPORTED")
        result=date(year,month,day)
    except ValueError as exc:raise ValueError("VOTE_DATE_INVALID") from exc
    return result.isoformat()
