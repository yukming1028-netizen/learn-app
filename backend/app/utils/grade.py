"""Grade calculation utilities."""
from datetime import datetime

GRADE_LABELS = {
    0: "小一學前預備",
    1: "小一",
    2: "小二",
    3: "小三",
    4: "小四",
    5: "小五",
    6: "小六",
}

MAX_GRADE = 6


def grade_label(grade: int) -> str:
    return GRADE_LABELS.get(grade, f"Grade {grade}")


def count_sept_firsts_since(base_date: datetime) -> int:
    """Count how many September 1sts have passed since base_date (up to now)."""
    now = datetime.utcnow()
    if base_date.tzinfo is not None:
        base_date = base_date.replace(tzinfo=None)
    
    count = 0
    for year in range(base_date.year, now.year + 1):
        sept_1 = datetime(year, 9, 1)
        if sept_1 > base_date and sept_1 <= now:
            count += 1
    return count


def check_grade_update(grade: int, grade_set_at: datetime, dismissed_at: datetime | None) -> dict:
    """Check if a grade update prompt should be shown.
    
    Returns: {
        "needs_prompt": bool,
        "suggested_grade": int,
        "current_grade": int,
        "suggested_label": str,
    }
    """
    # Base date for counting: dismissed_at if set, otherwise grade_set_at
    base_date = dismissed_at or grade_set_at
    if not base_date:
        return {"needs_prompt": False, "suggested_grade": grade, "current_grade": grade, "suggested_label": grade_label(grade)}
    
    sept_firsts = count_sept_firsts_since(base_date)
    suggested = min(grade + sept_firsts, MAX_GRADE)
    
    return {
        "needs_prompt": suggested > grade,
        "suggested_grade": suggested,
        "current_grade": grade,
        "suggested_label": grade_label(suggested),
    }
