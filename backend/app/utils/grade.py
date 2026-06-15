"""Grade calculation utilities."""
from datetime import datetime, timezone

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


def compute_current_grade(base_grade: int, base_date: datetime) -> tuple[int, str]:
    """Compute current grade based on base grade + date.
    
    Every September 1st since base_date, grade advances by 1.
    Caps at MAX_GRADE (6=小六).
    
    Returns (current_grade, label).
    """
    # Normalize: strip timezone to avoid naive vs aware comparison errors
    now = datetime.utcnow()
    if base_date.tzinfo is not None:
        base_date = base_date.replace(tzinfo=None)
    
    sept_firsts = 0
    for year in range(base_date.year, now.year + 1):
        sept_1 = datetime(year, 9, 1)
        if sept_1 > base_date and sept_1 <= now:
            sept_firsts += 1
    
    current_grade = min(base_grade + sept_firsts, MAX_GRADE)
    return current_grade, grade_label(current_grade)
