from typing import Literal, TypedDict


class ExpressionSeed(TypedDict):
    category: str
    expression: str
    common_alternative: str
    difficulty: Literal["beginner", "intermediate", "advanced"]


CURRICULUM: list[ExpressionSeed] = [
    # ── 정도 부사 (되게, 매우, 아주 대신) ──
    {"category": "adverb_degree", "expression": "자못", "common_alternative": "꽤/상당히", "difficulty": "intermediate"},
    {"category": "adverb_degree", "expression": "한껏", "common_alternative": "최대한/있는 힘껏", "difficulty": "beginner"},
    {"category": "adverb_degree", "expression": "심히", "common_alternative": "매우/심하게", "difficulty": "intermediate"},
    {"category": "adverb_degree", "expression": "사뭇", "common_alternative": "꽤/아주", "difficulty": "intermediate"},
    {"category": "adverb_degree", "expression": "더없이", "common_alternative": "더할 나위 없이/최고로", "difficulty": "beginner"},
    {"category": "adverb_degree", "expression": "여간", "common_alternative": "보통/웬만큼", "difficulty": "advanced"},
    {"category": "adverb_degree", "expression": "지극히", "common_alternative": "매우/극히", "difficulty": "beginner"},
    {"category": "adverb_degree", "expression": "무척", "common_alternative": "매우/아주", "difficulty": "beginner"},
    {"category": "adverb_degree", "expression": "몹시", "common_alternative": "매우/심하게", "difficulty": "beginner"},
    {"category": "adverb_degree", "expression": "제법", "common_alternative": "꽤/상당히", "difficulty": "beginner"},
    {"category": "adverb_degree", "expression": "가히", "common_alternative": "정말/참으로", "difficulty": "intermediate"},
    {"category": "adverb_degree", "expression": "썩", "common_alternative": "그다지/별로", "difficulty": "intermediate"},
    {"category": "adverb_degree", "expression": "퍽", "common_alternative": "매우/꽤", "difficulty": "intermediate"},
    {"category": "adverb_degree", "expression": "자뭇", "common_alternative": "거의/하마터면", "difficulty": "advanced"},
    {"category": "adverb_degree", "expression": "한결", "common_alternative": "훨씬/한층", "difficulty": "beginner"},

    # ── 양태 부사 (모양/상태 표현) ──
    {"category": "adverb_manner", "expression": "도리어", "common_alternative": "오히려", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "기어이", "common_alternative": "끝내/결국", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "이내", "common_alternative": "곧/바로", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "덩달아", "common_alternative": "따라서/같이", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "마냥", "common_alternative": "마치/계속", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "연신", "common_alternative": "계속/쉬지 않고", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "불현듯", "common_alternative": "갑자기/문득", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "무심결에", "common_alternative": "무의식적으로/나도 모르게", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "느닷없이", "common_alternative": "갑자기/뜬금없이", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "넌지시", "common_alternative": "슬쩍/은근히", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "슬며시", "common_alternative": "살짝/몰래", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "나지막이", "common_alternative": "낮게/조용히", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "고스란히", "common_alternative": "그대로/온전히", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "오롯이", "common_alternative": "온전히/오로지", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "저절로", "common_alternative": "자연스럽게/자동으로", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "선뜻", "common_alternative": "쉽게/망설임 없이", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "새삼", "common_alternative": "다시금/새롭게", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "난데없이", "common_alternative": "갑자기/뜬금없이", "difficulty": "intermediate"},
    {"category": "adverb_manner", "expression": "무작정", "common_alternative": "아무 생각 없이/막", "difficulty": "beginner"},
    {"category": "adverb_manner", "expression": "시나브로", "common_alternative": "서서히/모르는 사이에", "difficulty": "advanced"},

    # ── 수식어/관형어 ──
    {"category": "modifier", "expression": "무궁무진한", "common_alternative": "끝없는/많은", "difficulty": "beginner"},
    {"category": "modifier", "expression": "흡사한", "common_alternative": "비슷한/닮은", "difficulty": "beginner"},
    {"category": "modifier", "expression": "여실한", "common_alternative": "뚜렷한/분명한", "difficulty": "intermediate"},
    {"category": "modifier", "expression": "간곡한", "common_alternative": "간절한/진심 어린", "difficulty": "intermediate"},
    {"category": "modifier", "expression": "지대한", "common_alternative": "매우 큰", "difficulty": "beginner"},
    {"category": "modifier", "expression": "심상찮은", "common_alternative": "예사롭지 않은/보통이 아닌", "difficulty": "intermediate"},
    {"category": "modifier", "expression": "적잖은", "common_alternative": "적지 않은/꽤 많은", "difficulty": "beginner"},
    {"category": "modifier", "expression": "주도면밀한", "common_alternative": "꼼꼼한/치밀한", "difficulty": "intermediate"},
    {"category": "modifier", "expression": "고루한", "common_alternative": "낡은/구식의", "difficulty": "intermediate"},
    {"category": "modifier", "expression": "무던한", "common_alternative": "순한/별 탈 없는", "difficulty": "beginner"},
    {"category": "modifier", "expression": "가파른", "common_alternative": "급격한/빠른", "difficulty": "beginner"},
    {"category": "modifier", "expression": "미진한", "common_alternative": "부족한/아쉬운", "difficulty": "intermediate"},
    {"category": "modifier", "expression": "더딘", "common_alternative": "느린/느릿한", "difficulty": "beginner"},
    {"category": "modifier", "expression": "망연한", "common_alternative": "어이없는/멍한", "difficulty": "intermediate"},
    {"category": "modifier", "expression": "완강한", "common_alternative": "강한/굳센", "difficulty": "intermediate"},

    # ── 연결/서술 부사 ──
    {"category": "adverb_connective", "expression": "도무지", "common_alternative": "도저히/전혀", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "진작", "common_alternative": "미리/일찍", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "차마", "common_alternative": "감히/도저히", "difficulty": "intermediate"},
    {"category": "adverb_connective", "expression": "도대체", "common_alternative": "대체/영", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "하필", "common_alternative": "공교롭게/마침", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "비로소", "common_alternative": "그제야/드디어", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "미처", "common_alternative": "미리/사전에", "difficulty": "intermediate"},
    {"category": "adverb_connective", "expression": "차라리", "common_alternative": "그냥/오히려", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "여태", "common_alternative": "아직까지/지금까지", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "애당초", "common_alternative": "처음부터/원래", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "이윽고", "common_alternative": "마침내/드디어", "difficulty": "intermediate"},
    {"category": "adverb_connective", "expression": "기필코", "common_alternative": "반드시/꼭", "difficulty": "intermediate"},
    {"category": "adverb_connective", "expression": "대체로", "common_alternative": "보통/일반적으로", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "좀처럼", "common_alternative": "쉽게(~않다)", "difficulty": "beginner"},
    {"category": "adverb_connective", "expression": "고작", "common_alternative": "겨우/단지", "difficulty": "beginner"},

    # ── 사자성어/관용 표현 ──
    {"category": "idiom", "expression": "고진감래", "common_alternative": "고생 끝에 낙이 온다", "difficulty": "beginner"},
    {"category": "idiom", "expression": "각양각색", "common_alternative": "여러 가지/다양한", "difficulty": "beginner"},
    {"category": "idiom", "expression": "금상첨화", "common_alternative": "좋은 일에 또 좋은 일", "difficulty": "beginner"},
    {"category": "idiom", "expression": "사필귀정", "common_alternative": "결국 바른 길로", "difficulty": "intermediate"},
    {"category": "idiom", "expression": "자초지종", "common_alternative": "처음부터 끝까지", "difficulty": "beginner"},
    {"category": "idiom", "expression": "심심찮게", "common_alternative": "자주/꽤 많이", "difficulty": "intermediate"},
    {"category": "idiom", "expression": "대동소이", "common_alternative": "거의 비슷한", "difficulty": "beginner"},
    {"category": "idiom", "expression": "일거양득", "common_alternative": "한 번에 두 가지 이득", "difficulty": "beginner"},
    {"category": "idiom", "expression": "우여곡절", "common_alternative": "이런저런 어려움", "difficulty": "beginner"},
    {"category": "idiom", "expression": "시행착오", "common_alternative": "실패를 거듭하며 배움", "difficulty": "beginner"},
    {"category": "idiom", "expression": "동분서주", "common_alternative": "여기저기 바쁘게 뛰어다님", "difficulty": "intermediate"},
    {"category": "idiom", "expression": "전전긍긍", "common_alternative": "걱정하며 안절부절", "difficulty": "intermediate"},
    {"category": "idiom", "expression": "좌충우돌", "common_alternative": "이리저리 부딪히며", "difficulty": "beginner"},
    {"category": "idiom", "expression": "감개무량", "common_alternative": "감동이 매우 깊은", "difficulty": "intermediate"},
    {"category": "idiom", "expression": "백척간두", "common_alternative": "매우 위험한 상황", "difficulty": "advanced"},
]
