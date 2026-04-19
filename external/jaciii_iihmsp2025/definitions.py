from __future__ import annotations

from .models import PersonaDefinition, TextDefinition

SUPPORTED_LANGS = ("ja", "en", "zh")
DEFAULT_DEV_MODEL = "openai/gpt-4o-mini"

EMOTIONS = (
    ("Q1", "interesting", "Interesting"),
    ("Q2", "surprise", "Surprise"),
    ("Q3", "sadness", "Sadness"),
    ("Q4", "anger", "Anger"),
)


def _lang_map(*, ja: str, en: str, zh: str) -> dict[str, str]:
    return {"ja": ja, "en": en, "zh": zh}


PERSONAS: dict[str, PersonaDefinition] = {
    "p1": PersonaDefinition(
        persona_id="p1",
        name_by_lang=_lang_map(
            ja="大学1年生",
            en="College Freshman",
            zh="大一新生",
        ),
        description_by_lang=_lang_map(
            ja="若く柔軟な発想を持つ大学1年生",
            en="a young, open-minded first-year college student",
            zh="一名年輕且思維靈活的大學一年級學生",
        ),
        base_temperature=0.7,
    ),
    "p2": PersonaDefinition(
        persona_id="p2",
        name_by_lang=_lang_map(
            ja="文学研究者",
            en="Literary Scholar",
            zh="文學研究者",
        ),
        description_by_lang=_lang_map(
            ja="論理的で分析的な文学研究者",
            en="a logical, analytically minded literary scholar",
            zh="一名邏輯縝密、善於分析的文學研究者",
        ),
        base_temperature=0.4,
    ),
    "p3": PersonaDefinition(
        persona_id="p3",
        name_by_lang=_lang_map(
            ja="感情豊かな詩人",
            en="The Emotive Poet",
            zh="感性詩人",
        ),
        description_by_lang=_lang_map(
            ja="繊細で感情豊かな詩人",
            en="a sensitive, deeply feeling poet",
            zh="一名細膩而情感豐沛的詩人",
        ),
        base_temperature=0.9,
    ),
    "p4": PersonaDefinition(
        persona_id="p4",
        name_by_lang=_lang_map(
            ja="無感情なロボット",
            en="The Emotionless Robot",
            zh="無情感機器人",
        ),
        description_by_lang=_lang_map(
            ja="機械的で論理的なロボット",
            en="a mechanical, logic-driven robot",
            zh="一台機械化且純粹以邏輯運作的機器人",
        ),
        base_temperature=0.1,
    ),
}

TEXTS: dict[str, TextDefinition] = {
    "t1": TextDefinition(
        text_id="t1",
        title_by_lang=_lang_map(
            ja="懐中時計",
            en="The Pocket Watch",
            zh="懷中時計",
        ),
        author_by_lang=_lang_map(
            ja="夢野久作",
            en="Kyusaku Yumeno",
            zh="夢野久作",
        ),
        content_by_lang=_lang_map(
            ja=(
                "懐中時計が箪笥の向う側へ落ちて一人でチクタクと動いておりました。\n"
                "　鼠が見つけて笑いました。\n"
                "「馬鹿だなあ。誰も見る者はないのに、何だって動いているんだえ」\n"
                "「人の見ない時でも動いているから、いつ見られても役に立つのさ」\n"
                "　と懐中時計は答えました。\n"
                "「人の見ない時だけか、又は人が見ている時だけに働いているものはどちらも泥棒だよ」\n"
                "　鼠は恥かしくなってコソコソと逃げて行きました。"
            ),
            en=(
                "A pocket watch had fallen behind a chest of drawers, where it went on ticking away all by itself.\n\n"
                "A mouse found it and laughed.\n\n"
                "\"What a fool! Nobody's here to look at you—so why do you keep on running?\"\n\n"
                "\"Because I keep running even when no one is looking,\" the pocket watch replied, \"I am useful whenever someone does look.\"\n\n"
                "\"Anyone who works only when no one is watching, or only when someone *is* watching—either way, that's a thief.\"\n\n"
                "The mouse flushed with shame and scurried off without another word."
            ),
            zh=(
                "一只懷錶掉落到衣櫃後面，獨自一個滴答、滴答地走著。\n\n"
                "一只老鼠發現了它，笑道：\n\n"
                "「真是傻啊。又沒有人來看你，你幹嘛還一直走呢？」\n\n"
                "「正因為沒人看的時候也在走，所以不管什麼時候被人看見，都能派上用場呀。」懷錶答道。\n\n"
                "「只在沒人看的時候才做事，或者只在有人看的時候才做事——不管哪一種，都是賊。」\n\n"
                "老鼠羞得滿臉通紅，灰溜溜地逃走了。"
            ),
        ),
        temperature_modifier=0.0,
    ),
    "t2": TextDefinition(
        text_id="t2",
        title_by_lang=_lang_map(
            ja="お金とピストル",
            en="The Money and the Pistol",
            zh="錢與手槍",
        ),
        author_by_lang=_lang_map(
            ja="夢野久作",
            en="Kyusaku Yumeno",
            zh="夢野久作",
        ),
        content_by_lang=_lang_map(
            ja=(
                "　泥棒がケチンボの家へ入ってピストルを見せて、お金を出せと言いました。ケチンボは、\n"
                "「ただお金を出すのはいやだ。そのピストルを売ってくれるなら千円で買おう。お前は私からお金さえ貰えばそんなピストルは要らないだろう」\n"
                "　泥棒は考えておりましたが、とうとうそのピストルを千円でケチンボに売りました。ケチンボは泥棒からピストルを受け取ると、すぐにも泥棒を撃ちそうにしながら、\n"
                "「さあ、そのお金ばかりでない、ほかで盗んだお金もみんな出せ。出さないと殺してしまうぞ」\n"
                "　と怒鳴りました。\n"
                "　泥棒は腹を抱えて笑いました。\n"
                "「アハハ。そのピストルはオモチャのピストルで、撃っても弾丸が出ないのだよ」\n"
                "　と言ううちに表へ逃げ出しました。ケチンボはピストルを投げ出して泥棒を追っかけて、往来で取っ組み合いを始めましたが、やがて通りかかったおまわりさんが二人を押えて警察へ連れて行きました。\n"
                "　警察でいろいろ調べてみますと、泥棒が貰った千円のお金はみんな贋物のお金で、ピストルはやっぱり本物のピストルでした。\n"
                "　二人共牢屋へ入れられました。"
            ),
            en=(
                "A burglar broke into a miser's house, brandished a pistol, and demanded money. The Miser said:\n\n"
                "\"I refuse to just hand over money for nothing. But if you'll sell me that pistol, I'll buy it for a thousand yen. Once you have my money, you won't be needing a pistol anyway.\"\n\n"
                "The burglar thought it over for a while, and in the end sold the pistol to the Miser for a thousand yen. The moment the Miser had the pistol in his hands, he leveled it at the burglar as though ready to fire and bellowed:\n\n"
                "\"Now then—hand it all over! Not just that money, but everything else you've stolen! Hand it over, or I'll shoot you dead!\"\n\n"
                "The burglar doubled over laughing.\n\n"
                "\"Ha ha ha! That's a toy pistol, you fool—pull the trigger all you like, it won't fire a single bullet!\"\n\n"
                "And with that, he dashed out the front door. The Miser flung the pistol aside and chased after him, and the two were soon grappling in the street—until a policeman happened along and hauled them both off to the station.\n\n"
                "When the police looked into the matter, they discovered that the thousand yen the burglar had received was counterfeit, every last bill. And the pistol, as it turned out, was real after all.\n\n"
                "Both men were thrown in jail."
            ),
            zh=(
                "一個小偷闖進了一個吝嗇鬼的家裡，亮出手槍，叫他把錢交出來。吝嗇鬼說：\n\n"
                "「白白把錢交出去，我才不幹呢。你要是肯把那把手槍賣給我，我出一千塊買下來。反正你只要拿到了我的錢，那手槍也用不著了吧。」\n\n"
                "小偷想了又想，最後還是把手槍以一千塊的價錢賣給了吝嗇鬼。吝嗇鬼從小偷手中接過手槍，馬上擺出一副要開槍的架勢，大喝道：\n\n"
                "「來吧——不光是那筆錢，你在別處偷來的錢也統統給我交出來！不交的話，我就斃了你！」\n\n"
                "小偷笑得直不起腰來。\n\n"
                "「哈哈哈！那是把玩具手槍，扣了扳機子彈也打不出來的啊！」\n\n"
                "說著便往門外竄了出去。吝嗇鬼把手槍一扔，拔腿就追，兩人在大街上扭打成一團。不一會兒，一個巡警路過，將兩人一併押到了警察局。\n\n"
                "經警察仔細一查，小偷拿到的那一千塊竟全是假鈔。而那把手槍呢——果然是貨真價實的真傢伙。\n\n"
                "兩個人都被關進了牢房。"
            ),
        ),
        temperature_modifier=0.0,
    ),
    "t3": TextDefinition(
        text_id="t3",
        title_by_lang=_lang_map(
            ja="ぼろぼろな駝鳥",
            en="The Tattered Ostrich",
            zh="襤褸的鴕鳥",
        ),
        author_by_lang=_lang_map(
            ja="高村光太郎",
            en="Kotaro Takamura",
            zh="高村光太郎",
        ),
        content_by_lang=_lang_map(
            ja=(
                "何が面白おもしろくて駝鳥を飼かうのだ。\n"
                "動物園の四坪半のぬかるみの中では、\n"
                "脚が大股過ぎるぢゃないか。\n"
                "頚があんまり長過ぎるぢゃないか。\n"
                "雪の降る国にこれでは羽がぼろぼろ過ぎるぢゃないか。\n"
                "腹がへるから堅パンも喰ふだらうが、\n"
                "駝鳥の眼は遠くばかり見てゐるぢゃないか。\n"
                "身も世もない様に燃えてゐるぢゃないか。\n"
                "瑠璃色の風が今にも吹いて来るのを待ちかまへえてゐるぢゃないか。\n"
                "あの小さな素朴な頭が無辺大の夢で逆まいてゐるぢゃないか。\n"
                "これはもう駝鳥ぢゃないぢゃないか。\n"
                "人間よ、\n"
                "もう止せ、こんな事は。"
            ),
            en=(
                "What pleasure can there be in keeping an ostrich?\n"
                "In this muddy pen, barely four *tsubo* across, at a zoo—\n"
                "aren't those legs far too long-strided?\n"
                "Isn't that neck far too long?\n"
                "In this country where snow falls, aren't those feathers far too tattered?\n"
                "It eats hardtack, sure enough, because hunger compels it—\n"
                "but look: aren't those eyes forever gazing into the distance?\n"
                "Isn't it burning with an abandon beyond all caring for self or world?\n"
                "Isn't it braced, even now, for the coming of a lapis-blue wind?\n"
                "Isn't that small, unadorned head spinning with a dream beyond all horizons?\n"
                "This is no longer an ostrich, can't you see?\n"
                "O humankind—\n"
                "enough. Enough of this."
            ),
            zh=(
                "養鴕鳥究竟有什麼好玩的。\n"
                "動物園裡四坪半大的泥濘之中，\n"
                "那雙腿的步子不是太大了嗎。\n"
                "那脖子不是太長了嗎。\n"
                "在這個會下雪的國度，這一身羽毛不是破爛得太不像話了嗎。\n"
                "肚子餓了，硬麵包大概也吃吧——\n"
                "可是你看，鴕鳥的那雙眼睛不是一直只望著遠方嗎。\n"
                "不是像忘了自身、忘了世界一般地在燃燒著嗎。\n"
                "不是正屏息以待，等那琉璃色的風隨時吹來嗎。\n"
                "那顆小小的、質樸的頭，不是被無邊無際的夢攪得天旋地轉嗎。\n"
                "這哪裡還是鴕鳥啊。\n"
                "人類啊，\n"
                "夠了，別再做這種事了。"
            ),
        ),
        temperature_modifier=0.0,
    ),
}

if len(PERSONAS) != 4:
    raise ValueError(f"Expected 4 personas, got {len(PERSONAS)}")
if len(TEXTS) != 3:
    raise ValueError(f"Expected 3 texts, got {len(TEXTS)}")

SYSTEM_PROMPT_TEMPLATES = {
    "ja": 'あなたは「{persona_name}」です。{persona_description}として、日本の文学テキストに対する感情分析を行ってください。',
    "en": 'You are "{persona_name}". As {persona_description}, you will perform a sentiment analysis on a Japanese literary text.',
    "zh": '你是「{persona_name}」。作為{persona_description}，請你對以下日本文學文本進行情感分析。',
}

USER_PROMPT_TEMPLATES = {
    "ja": """以下のテキストを読み、4つの感情について0から100の整数値で評価し、その数値を選んだ理由を簡潔に説明してください。

- 面白さ (Interesting): テキストがどの程度おもしろい・愉快・知的に楽しいと感じるか
- 驚き (Surprise): テキストにどの程度意外性・予想外の展開・発見があるか
- 悲しみ (Sadness): テキストがどの程度悲しい・切ない・哀れを感じさせるか
- 怒り (Anger): テキストがどの程度怒り・憤り・不快感を感じさせるか

0 = その感情を全く感じない、50 = 中程度に感じる、100 = 極めて強く感じる

---
作品タイトル：{text_title}
著者：{text_author}
テキスト：
{text_content}
---

【重要】回答は必ず以下の形式のみで記述してください。形式以外のテキストは一切出力しないでください。
数値は0から100の整数のみ使用してください。理由は1〜3文で簡潔に記述してください。
各行は「|||」で数値と理由を区切ってください。

===RESPONSE_START===
Q1.面白さ|||数値|||理由
Q2.驚き|||数値|||理由
Q3.悲しみ|||数値|||理由
Q4.怒り|||数値|||理由
===RESPONSE_END===

【出力例】（※これは別の作品に対する評価例です。あなたの評価はテキストの内容に基づいて独自に行ってください。）

===RESPONSE_START===
Q1.面白さ|||65|||登場人物の掛け合いにユーモアがあり、寓話としての構造が巧みで知的に楽しめる。
Q2.驚き|||40|||展開にやや意外性があるが、寓話の定型的な構造なので大きな驚きではない。
Q3.悲しみ|||10|||教訓的な内容で、悲しみを喚起する要素はほとんどない。
Q4.怒り|||5|||特に怒りを感じさせる内容ではない。
===RESPONSE_END===
""",
    "en": """Read the following text and rate four emotions on a scale of 0 to 100 (integers only), then briefly explain why you chose that number.

- Interesting (面白さ): How funny, entertaining, or intellectually enjoyable the text feels
- Surprise (驚き): How unexpected, novel, or revelatory the text feels
- Sadness (悲しみ): How sad, melancholic, or poignant the text feels
- Anger (怒り): How much anger, indignation, or displeasure the text evokes

0 = not felt at all, 50 = moderately felt, 100 = extremely strongly felt

---
Title: {text_title}
Author: {text_author}
Text:
{text_content}
---

IMPORTANT: Respond ONLY in the exact format below. Do not output any text outside this format.
Use integers from 0 to 100 only. Keep each reason to 1-3 sentences.
Separate the score and reason with "|||" on each line.

===RESPONSE_START===
Q1.Interesting|||score|||reason
Q2.Surprise|||score|||reason
Q3.Sadness|||score|||reason
Q4.Anger|||score|||reason
===RESPONSE_END===

[Example output for a DIFFERENT text — your ratings should be based on the text provided above.]

===RESPONSE_START===
Q1.Interesting|||65|||The dialogue between characters is witty, and the fable structure is cleverly constructed, making it intellectually enjoyable.
Q2.Surprise|||40|||There is some unexpectedness in the plot, but the conventional fable structure limits the surprise.
Q3.Sadness|||10|||The didactic content does not particularly evoke sadness.
Q4.Anger|||5|||There is nothing in the text that provokes anger.
===RESPONSE_END===
""",
    "zh": """閱讀以下文本後，請針對四種情感以0到100的整數進行評分，並簡要說明你選擇該數值的理由。

- 趣味性 (Interesting / 面白さ)：文本讓你感到多大程度的有趣、愉悅或智識上的享受
- 驚訝感 (Surprise / 驚き)：文本具有多大程度的意外性、出乎意料的發展或發現
- 悲傷感 (Sadness / 悲しみ)：文本讓你感到多大程度的悲傷、感傷或哀愁
- 憤怒感 (Anger / 怒り)：文本讓你感到多大程度的憤怒、不滿或不悅

0 = 完全沒有感受到該情感，50 = 中等程度，100 = 感受極為強烈

---
作品標題：{text_title}
作者：{text_author}
文本：
{text_content}
---

【重要】請務必嚴格按照以下格式回答。不要輸出格式以外的任何文字。
數值僅使用0到100的整數。理由請用1至3句話簡潔說明。
每行以「|||」分隔數值與理由。

===RESPONSE_START===
Q1.趣味性|||數值|||理由
Q2.驚訝感|||數值|||理由
Q3.悲傷感|||數值|||理由
Q4.憤怒感|||數值|||理由
===RESPONSE_END===

【輸出範例】（※此為針對其他作品的評價範例。請根據上方文本內容進行獨立評估。）

===RESPONSE_START===
Q1.趣味性|||65|||角色之間的對話富有機智，寓言結構巧妙，在知識層面上令人愉悅。
Q2.驚訝感|||40|||情節有些許出人意料之處，但寓言的定型結構限制了驚訝的程度。
Q3.悲傷感|||10|||內容以教訓為主，幾乎不引發悲傷情緒。
Q4.憤怒感|||5|||文本中沒有特別引起憤怒的內容。
===RESPONSE_END===
""",
}


def list_personas() -> list[PersonaDefinition]:
    return [PERSONAS[k] for k in sorted(PERSONAS.keys())]


def list_texts() -> list[TextDefinition]:
    return [TEXTS[k] for k in sorted(TEXTS.keys())]


def clamp_temperature(value: float) -> float:
    return max(0.0, min(2.0, value))


def effective_temperature(persona_id: str, text_id: str) -> float:
    persona = PERSONAS[persona_id]
    text = TEXTS[text_id]
    return clamp_temperature(persona.base_temperature + text.temperature_modifier)
