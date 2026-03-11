from typing import Literal, TypedDict


class ClusterSeed(TypedDict):
    category: str
    base_word: str
    expressions: list[str]
    difficulty: Literal["beginner", "intermediate", "advanced"]


CURRICULUM: list[ClusterSeed] = [
    # ── 정도 부사 (3) ──
    {
        "category": "adverb_degree",
        "base_word": "매우/되게",
        "expressions": ["자못", "한껏", "사뭇", "더없이", "지극히"],
        "difficulty": "beginner",
    },
    {
        "category": "adverb_degree",
        "base_word": "꽤/상당히",
        "expressions": ["제법", "여간", "가히", "퍽", "한결"],
        "difficulty": "intermediate",
    },
    {
        "category": "adverb_degree",
        "base_word": "별로/안",
        "expressions": ["썩", "좀처럼", "고작", "여태", "미처"],
        "difficulty": "intermediate",
    },

    # ── 양태 부사 (6) ──
    {
        "category": "adverb_manner",
        "base_word": "갑자기",
        "expressions": ["불현듯", "느닷없이", "난데없이", "무심결에", "선뜻"],
        "difficulty": "beginner",
    },
    {
        "category": "adverb_manner",
        "base_word": "몰래/살짝",
        "expressions": ["슬며시", "넌지시", "나지막이", "시나브로", "은근슬쩍"],
        "difficulty": "beginner",
    },
    {
        "category": "adverb_manner",
        "base_word": "계속/자꾸",
        "expressions": ["연신", "마냥", "덩달아", "무작정", "기어이"],
        "difficulty": "intermediate",
    },
    {
        "category": "adverb_manner",
        "base_word": "그대로/온전히",
        "expressions": ["고스란히", "오롯이", "저절로", "이내", "새삼"],
        "difficulty": "beginner",
    },
    {
        "category": "adverb_manner",
        "base_word": "오히려",
        "expressions": ["도리어", "차라리", "하필", "애당초", "도무지"],
        "difficulty": "intermediate",
    },
    {
        "category": "adverb_manner",
        "base_word": "꼭/반드시",
        "expressions": ["기필코", "차마", "비로소", "이윽고", "진작"],
        "difficulty": "intermediate",
    },

    # ── 시간 부사 (3) ──
    {
        "category": "adverb_time",
        "base_word": "결국/드디어",
        "expressions": ["기어이", "이윽고", "비로소", "마침내", "끝내"],
        "difficulty": "beginner",
    },
    {
        "category": "adverb_time",
        "base_word": "미리/일찍",
        "expressions": ["진작", "미처", "애당초", "사전에", "일찌감치"],
        "difficulty": "beginner",
    },
    {
        "category": "adverb_time",
        "base_word": "다시/새롭게",
        "expressions": ["새삼", "거듭", "재차", "다시금", "또다시"],
        "difficulty": "beginner",
    },

    # ── 강조/의문 (1) ──
    {
        "category": "adverb_emphasis",
        "base_word": "대체/도저히",
        "expressions": ["도무지", "도대체", "차마", "감히", "여간"],
        "difficulty": "intermediate",
    },

    # ── 관형어 (4) ──
    {
        "category": "modifier",
        "base_word": "큰/엄청난",
        "expressions": ["지대한", "막대한", "무궁무진한", "가파른", "심상찮은"],
        "difficulty": "beginner",
    },
    {
        "category": "modifier",
        "base_word": "정확한/확실한",
        "expressions": ["여실한", "주도면밀한", "완강한", "간곡한", "적확한"],
        "difficulty": "intermediate",
    },
    {
        "category": "modifier",
        "base_word": "부족한/아쉬운",
        "expressions": ["미진한", "더딘", "적잖은", "고루한", "망연한"],
        "difficulty": "intermediate",
    },
    {
        "category": "modifier",
        "base_word": "비슷한/같은",
        "expressions": ["흡사한", "대동소이한", "무던한", "유사한", "동일한"],
        "difficulty": "beginner",
    },

    # ── 사자성어 (3) ──
    {
        "category": "idiom",
        "base_word": "노력과 보상",
        "expressions": ["고진감래", "금상첨화", "일거양득", "사필귀정", "감개무량"],
        "difficulty": "beginner",
    },
    {
        "category": "idiom",
        "base_word": "어려움과 분투",
        "expressions": ["우여곡절", "전전긍긍", "좌충우돌", "동분서주", "백척간두"],
        "difficulty": "intermediate",
    },
    {
        "category": "idiom",
        "base_word": "다양함과 과정",
        "expressions": ["각양각색", "시행착오", "자초지종", "심심찮게", "대동소이"],
        "difficulty": "beginner",
    },
]
