"""AI Question Generator — template-based intelligent question generation.

Generates questions from curriculum templates covering:
- Math: arithmetic, fractions, geometry, word problems
- Chinese: idioms, antonyms, fill-blank
- English: vocabulary, grammar, translation
- Science: concepts, classification

Each generated question follows the Question model schema.
Questions are marked status='pending' for review before going live.
"""
import random
import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class GeneratedQuestion:
    subject: str
    grade: int
    difficulty: int
    type: str  # choice, input, fill_blank
    content: str
    options: list
    answer: str
    explanation: str
    tags: list
    avg_time_sec: float


# ──────────────────────────────────────────────
# MATH generators
# ──────────────────────────────────────────────

def _gen_addition(grade: int, difficulty: int) -> GeneratedQuestion:
    if grade <= 1:
        a, b = random.randint(1, 9), random.randint(1, 9)
    elif grade <= 2:
        a, b = random.randint(10, 50), random.randint(10, 50)
    elif grade <= 3:
        a, b = random.randint(100, 500), random.randint(100, 500)
    else:
        a, b = random.randint(1000, 9999), random.randint(1000, 9999)

    ans = a + b
    opts = _make_options(str(ans), range_val=max(ans // 4, 5))
    return GeneratedQuestion(
        subject="math", grade=grade, difficulty=difficulty,
        type="choice", content=f"{a} + {b} = ?",
        options=opts, answer=str(ans),
        explanation=f"{a} 加 {b} 等於 {ans}",
        tags=["加法", f"{'個位數' if grade <= 1 else '多位數'}"],
        avg_time_sec=15.0 + grade * 3,
    )


def _gen_subtraction(grade: int, difficulty: int) -> GeneratedQuestion:
    if grade <= 1:
        a = random.randint(5, 18)
        b = random.randint(1, a)
    elif grade <= 2:
        a = random.randint(20, 99)
        b = random.randint(1, a)
    else:
        a = random.randint(100, 999)
        b = random.randint(10, a)

    ans = a - b
    opts = _make_options(str(ans), range_val=max(ans // 4, 5))
    return GeneratedQuestion(
        subject="math", grade=grade, difficulty=difficulty,
        type="choice", content=f"{a} − {b} = ?",
        options=opts, answer=str(ans),
        explanation=f"{a} 減 {b} 等於 {ans}",
        tags=["減法"],
        avg_time_sec=15.0 + grade * 3,
    )


def _gen_multiplication(grade: int, difficulty: int) -> GeneratedQuestion:
    if grade <= 2:
        a, b = random.randint(2, 9), random.randint(2, 9)
    else:
        a, b = random.randint(6, 12), random.randint(6, 12)

    ans = a * b
    opts = _make_options(str(ans), range_val=max(ans // 4, 5))
    return GeneratedQuestion(
        subject="math", grade=grade, difficulty=difficulty,
        type="choice", content=f"{a} × {b} = ?",
        options=opts, answer=str(ans),
        explanation=f"{a} 乘以 {b} 等於 {ans}",
        tags=["乘法", "九九乘法"],
        avg_time_sec=20.0,
    )


def _gen_division(grade: int, difficulty: int) -> GeneratedQuestion:
    b = random.randint(2, 9)
    quotient = random.randint(2, 12)
    a = b * quotient  # ensure clean division

    opts = _make_options(str(quotient), range_val=max(quotient, 5))
    return GeneratedQuestion(
        subject="math", grade=grade, difficulty=difficulty,
        type="choice", content=f"{a} ÷ {b} = ?",
        options=opts, answer=str(quotient),
        explanation=f"{a} 除以 {b} 等於 {quotient}",
        tags=["除法"],
        avg_time_sec=20.0,
    )


def _gen_fill_blank_math(grade: int, difficulty: int) -> GeneratedQuestion:
    templates = [
        ("___ + ___ = 10", lambda: _pair_sum(10), "兩個數加起來等於10"),
        ("___ × ___ = 24", lambda: _pair_product(24), "兩個數乘起來等於24"),
        ("___ 比 5 大，比 8 小", lambda: random.choice([6, 7]), "5和8之間的數"),
        ("100 − ___ = 37", lambda: 63, "100減63等於37"),
    ]
    if grade >= 3:
        templates += [
            ("___ ÷ 6 = 7，餘數是 ___", lambda: f"42|0", "42÷6=7餘0"),
            ("長方形面積 = ___ × ___", lambda: "長|寬", "長方形面積公式"),
        ]

    content, gen_fn, expl = random.choice(templates)
    answer = gen_fn()
    return GeneratedQuestion(
        subject="math", grade=grade, difficulty=difficulty,
        type="fill_blank", content=content,
        options=[], answer=str(answer),
        explanation=expl,
        tags=["填空", "數學概念"],
        avg_time_sec=25.0,
    )


# ──────────────────────────────────────────────
# CHINESE generators
# ──────────────────────────────────────────────

CHINESE_OPPOSITES = [
    ("大", "小"), ("高", "矮"), ("長", "短"), ("快", "慢"),
    ("多", "少"), ("黑", "白"), ("好", "壞"), ("冷", "熱"),
    ("開", "關"), ("來", "去"), ("上", "下"), ("前", "後"),
]

CHINESE_SYNONYMS = [
    ("快樂", "高興"), ("美麗", "漂亮"), ("勇敢", "英勇"),
    ("簡單", "容易"), ("開心", "高興"), ("聰明", "機智"),
]

CHINESE_IDIOMS = [
    ("一___兩得", "石", "一石兩得：一個舉動得到兩種好處"),
    ("___不可失", "機", "機不可失：好機會不能錯過"),
    ("畫___添足", "蛇", "畫蛇添足：多餘的行為反而不好"),
    ("亡___補牢", "羊", "亡羊補牢：出問題後及時補救"),
    ("守株待___", "兔", "守株待兔：不努力只等運氣"),
]


def _gen_chinese_opposite(grade: int, difficulty: int) -> GeneratedQuestion:
    word, opp = random.choice(CHINESE_OPPOSITES)
    other = [o for w, o in CHINESE_OPPOSITES if o != opp][:3]
    opts = other[:3] + [opp]
    random.shuffle(opts)
    return GeneratedQuestion(
        subject="chinese", grade=grade, difficulty=difficulty,
        type="choice", content=f"「{word}」的反義詞是？",
        options=opts, answer=opp,
        explanation=f"{word} 和 {opp} 是反義詞",
        tags=["反義詞"],
        avg_time_sec=12.0,
    )


def _gen_chinese_synonym(grade: int, difficulty: int) -> GeneratedQuestion:
    word, syn = random.choice(CHINESE_SYNONYMS)
    others = [s for w, s in CHINESE_SYNONYMS if s != syn][:3]
    opts = others + [syn]
    random.shuffle(opts)
    return GeneratedQuestion(
        subject="chinese", grade=grade, difficulty=difficulty,
        type="choice", content=f"「{word}」的近義詞是？",
        options=opts, answer=syn,
        explanation=f"{word} 和 {syn} 意思相近",
        tags=["近義詞"],
        avg_time_sec=12.0,
    )


def _gen_chinese_idiom(grade: int, difficulty: int) -> GeneratedQuestion:
    partial, char, expl = random.choice(CHINESE_IDIOMS)
    wrong_chars = ["天", "地", "人", "心", "風", "雲", "馬", "龍"]
    wrong = random.sample([c for c in wrong_chars if c != char], 3)
    opts = wrong + [char]
    random.shuffle(opts)
    return GeneratedQuestion(
        subject="chinese", grade=grade, difficulty=difficulty,
        type="choice", content=f"填入正確的字：「{partial}」",
        options=opts, answer=char,
        explanation=expl,
        tags=["成語", "填空"],
        avg_time_sec=15.0,
    )


# ──────────────────────────────────────────────
# ENGLISH generators
# ──────────────────────────────────────────────

EN_VOCAB = [
    ("蘋果", "apple", "🍎"), ("香蕉", "banana", "🍌"), ("貓", "cat", "🐱"),
    ("狗", "dog", "🐶"), ("書", "book", "📚"), ("水", "water", "💧"),
    ("紅色", "red", "🔴"), ("藍色", "blue", "🔵"), ("星期一", "Monday", "📅"),
    ("老師", "teacher", "👩‍🏫"), ("學校", "school", "🏫"), ("朋友", "friend", "🤝"),
]

EN_OPPOSITES = [
    ("hot", "cold"), ("big", "small"), ("happy", "sad"),
    ("fast", "slow"), ("up", "down"), ("open", "close"),
    ("day", "night"), ("good", "bad"),
]


def _gen_en_vocab(grade: int, difficulty: int) -> GeneratedQuestion:
    cn, en, emoji = random.choice(EN_VOCAB)
    others = [e for _, e, _ in EN_VOCAB if e != en]
    wrong = random.sample(others, 3)
    opts = wrong + [en]
    random.shuffle(opts)
    return GeneratedQuestion(
        subject="english", grade=grade, difficulty=difficulty,
        type="choice", content=f'"{cn}{emoji}" 的英文是？',
        options=opts, answer=en,
        explanation=f"{cn} = {en} {emoji}",
        tags=["vocabulary"],
        avg_time_sec=12.0,
    )


def _gen_en_opposite(grade: int, difficulty: int) -> GeneratedQuestion:
    word, opp = random.choice(EN_OPPOSITES)
    others = [o for _, o in EN_OPPOSITES if o != opp][:3]
    opts = others + [opp]
    random.shuffle(opts)
    return GeneratedQuestion(
        subject="english", grade=grade, difficulty=difficulty,
        type="choice", content=f'The opposite of "{word}" is ___',
        options=opts, answer=opp,
        explanation=f'{word} ↔ {opp}',
        tags=["opposites", "vocabulary"],
        avg_time_sec=15.0,
    )


def _gen_en_fill_blank(grade: int, difficulty: int) -> GeneratedQuestion:
    templates = [
        ('I have two ___ (手).', "hands", "hand的複數是hands"),
        ('She ___ (go/過去式) to school.', "went", "go的過去式是went"),
        ('There ___ (is/are) five apples.', "are", "複數名詞用are"),
        ('The opposite of "big" is ___.', "small", "big的反義詞"),
    ]
    content, answer, expl = random.choice(templates)
    return GeneratedQuestion(
        subject="english", grade=grade, difficulty=difficulty,
        type="fill_blank", content=content,
        options=[], answer=answer,
        explanation=expl,
        tags=["grammar", "fill_blank"],
        avg_time_sec=15.0,
    )


# ──────────────────────────────────────────────
# SCIENCE generators
# ──────────────────────────────────────────────

SCIENCE_FACTS = [
    ("水在幾度結冰？", ["0°C", "10°C", "50°C", "100°C"], "0°C", "水的冰點是0°C"),
    ("彩虹有幾種顏色？", ["5種", "6種", "7種", "8種"], "7種", "紅橙黃綠藍靛紫"),
    ("太陽從哪個方向升起？", ["東邊", "西邊", "北邊", "南邊"], "東邊", "太陽東升西落"),
    ("蜻蜓有幾隻腳？", ["4隻", "6隻", "8隻", "10隻"], "6隻", "昆蟲都有6隻腳"),
    ("地球繞太陽一圈要多久？", ["一天", "一個月", "一年", "十年"], "一年", "地球公轉一周約365天"),
    ("植物靠什麼製造養分？", ["呼吸作用", "光合作用", "蒸散作用", "消化作用"], "光合作用", "光合作用需要陽光和水"),
    ("下列哪個不是哺乳動物？", ["狗", "貓", "企鵝", "鯨魚"], "企鵝", "企鵝是鳥類"),
    ("磁鐵哪裡吸力最強？", ["中間", "兩極", "側面", "都一樣"], "兩極", "南極和北極磁力最強"),
]


def _gen_science(grade: int, difficulty: int) -> GeneratedQuestion:
    content, opts, answer, expl = random.choice(SCIENCE_FACTS)
    shuffled = opts.copy()
    random.shuffle(shuffled)
    return GeneratedQuestion(
        subject="science", grade=grade, difficulty=difficulty,
        type="choice", content=content,
        options=shuffled, answer=answer,
        explanation=expl,
        tags=["科學知識"],
        avg_time_sec=18.0,
    )


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _make_options(answer: str, range_val: int = 5) -> list:
    """Generate 3 wrong options + correct answer, shuffled."""
    ans_num = int(answer)
    wrongs = set()
    attempts = 0
    while len(wrongs) < 3 and attempts < 20:
        offset = random.randint(-range_val, range_val)
        val = ans_num + offset
        if val != ans_num and val > 0:
            wrongs.add(str(val))
        attempts += 1
    while len(wrongs) < 3:
        wrongs.add(str(ans_num + len(wrongs) + 1))
    opts = list(wrongs) + [answer]
    random.shuffle(opts)
    return opts


def _pair_sum(target: int) -> str:
    a = random.randint(1, target - 1)
    return f"{a}|{target - a}"


def _pair_product(target: int) -> str:
    factors = [(i, target // i) for i in range(2, target) if target % i == 0]
    if factors:
        a, b = random.choice(factors)
        return f"{a}|{b}"
    return f"1|{target}"


# ──────────────────────────────────────────────
# Main generator dispatcher
# ──────────────────────────────────────────────

GENERATORS = {
    ("math", "addition"): _gen_addition,
    ("math", "subtraction"): _gen_subtraction,
    ("math", "multiplication"): _gen_multiplication,
    ("math", "division"): _gen_division,
    ("math", "fill_blank"): _gen_fill_blank_math,
    ("chinese", "opposite"): _gen_chinese_opposite,
    ("chinese", "synonym"): _gen_chinese_synonym,
    ("chinese", "idiom"): _gen_chinese_idiom,
    ("english", "vocabulary"): _gen_en_vocab,
    ("english", "opposite"): _gen_en_opposite,
    ("english", "fill_blank"): _gen_en_fill_blank,
    ("science", "general"): _gen_science,
}

SUBJECT_TOPICS = {
    "math": ["addition", "subtraction", "multiplication", "division", "fill_blank"],
    "chinese": ["opposite", "synonym", "idiom"],
    "english": ["vocabulary", "opposite", "fill_blank"],
    "science": ["general"],
}


def generate_questions(
    subject: str,
    grade: int,
    topic: Optional[str] = None,
    count: int = 5,
    difficulty: Optional[int] = None,
) -> list[GeneratedQuestion]:
    """Generate N questions for given subject/grade/topic."""
    results = []
    topics = [topic] if topic else SUBJECT_TOPICS.get(subject, ["general"])

    for _ in range(count):
        t = random.choice(topics)
        key = (subject, t)
        gen_fn = GENERATORS.get(key)
        if not gen_fn:
            continue
        diff = difficulty or random.randint(1, min(grade + 1, 5))
        q = gen_fn(grade, diff)
        results.append(q)

    return results
