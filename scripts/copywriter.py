# -*- coding: utf-8 -*-
"""闽南语播报文案（台罗拼音 + 标点级停顿控制）。

核心设计：MMS 模型对句内逗号几乎不停顿，因此把停顿权完全拿回来自控——
文案按"标点碎片"切分，每个碎片独立合成，碎片之间插入固定静音：
  逗号/顿号  -> 0.35s
  句号/冒号  -> 0.60s
  感叹号      -> 0.50s
最终拼接时按碎片标点类型插入对应停顿，节奏完全可预期。

产出结构：pieces = [(text, pause_after_seconds), ...]，由 tts_mms.synthesize 消费。
"""
import datetime
import re

# ---- 数字转台罗（0~99，白读）----
# 数字白读表：1 在 11/21/31 等个位用文读 it（十一=cha̍p-it），其余用白读
_NUM = {
    0: "líng", 1: "it", 2: "jī", 3: "sann", 4: "sì", 5: "gōo",
    6: "la̍k", 7: "tshit", 8: "peh", 9: "káu",
}
_TENS = {2: "jī", 3: "saⁿ", 4: "sì", 5: "gōo", 6: "la̍k", 7: "tshit", 8: "peh", 9: "káu"}


def num2tailo(n: int) -> str:
    n = int(n)
    if n < 0:
        return "līng-hā " + num2tailo(-n)
    if n < 10:
        return _NUM[n]
    if n < 20:
        return "cha̍p" + ("-" + _NUM[n % 10] if n % 10 else "")
    t = _TENS[n // 10]
    r = n % 10
    return f"{t}-tsa̍p" + (f"-{_NUM[r]}" if r else "")


# ---- 星期 / 月份（用户选定：礼拜= lé-pài）----
WEEKDAY_TAILO = ["lé-pài-it", "lé-pài-jī", "lé-pài-sann", "lé-pài-sù", "lé-pài-gōo", "lé-pài-la̍k", "lé-pài-ji̍t"]
WEEKDAY_CN = ["礼拜一", "礼拜二", "礼拜三", "礼拜四", "礼拜五", "礼拜六", "礼拜日"]
_MONTH_TAILO = {
    1: "it-gue̍h", 2: "jī-gue̍h", 3: "sann-gue̍h", 4: "sì-gue̍h", 5: "gōo-gue̍h",
    6: "la̍k-gue̍h", 7: "tshit-gue̍h", 8: "peh-gue̍h", 9: "káu-gue̍h",
    10: "cha̍p-gue̍h", 11: "cha̍p-it-gue̍h", 12: "cha̍p-jī-gue̍h",
}

# ---- 天气现象 → 台罗 ----
WEATHER_TAILO = {
    "晴": "tsîng", "多云": "to-hûn", "阴": "im", "阴天": "im-thiⁿ",
    "小雨": "sió-hōo", "中雨": "tiong-hōo", "大雨": "tuā-hōo",
    "暴雨": "pō-hōo", "阵雨": "tsūn-hōo", "雷阵雨": "luî-tsūn-hōo",
    "雷雨": "luî-hōo", "雷暴": "luî-pō", "雨": "hōo", "雪": "seh",
    "小雪": "sió-seh", "中雪": "tiong-seh", "大雪": "tuā-seh", "雨夹雪": "hōo-kah-seh",
    "雾": "bū", "霾": "bâi", "霜冻": "sng-tàng", "冰雹": "ping-pha̍k",
    "台风": "hong-thai", "阵风": "tsūn-hong", "大风": "tuā-hong",
    "晴转多云": "tsîng tsùan to-hûn", "晴转阴": "tsîng tsùan im",
    "多云转晴": "to-hûn tsùan tsîng", "多云转阴": "to-hûn tsùan im",
    "阴转晴": "im tsùan tsîng", "阴转多云": "im tsùan to-hûn",
    "小雨转多云": "sió-hōo tsùan to-hûn", "阵雨转多云": "tsūn-hōo tsùan to-hûn",
}

# ---- 风向 → 台罗 ----
WIND_TAILO = {
    "北风": "pak-hong", "南风": "lâm-hong", "东风": "tang-hong", "西风": "sai-hong",
    "东北风": "tang-pak-hong", "东南风": "tang-lâm-hong",
    "西北风": "sai-pak-hong", "西南风": "sai-lâm-hong",
    "北": "pak-hong", "南": "lâm-hong", "东": "tang-hong", "西": "sai-hong",
    "东北": "tang-pak-hong", "东南": "tang-lâm-hong",
    "西北": "sai-pak-hong", "西南": "sai-lâm-hong",
}

# 停顿时长（秒）：逗号短停、句号长停
_PAUSE_COMMA = 0.35
_PAUSE_PERIOD = 0.60
_PAUSE_EXCLAM = 0.50
_PAUSE_COLON = 0.45
_ENDING_PAUSE = 0.75  # 最后收尾句的尾停

_RAIN_WORDS = ("雨", "阵雨", "雷", "冰雹")


def _is_rain(w: str) -> bool:
    return any(k in w for k in _RAIN_WORDS)


def _weather_tailo(w: str) -> str:
    if not w:
        return "bô-hong-bô-hōo"
    w = w.strip()
    return WEATHER_TAILO.get(w, "tsîng")


def _split_pieces(text: str, end_pause: float = None) -> list:
    """把一句台罗文本按标点拆成 (fragment, pause_after) 碎片。

    标点规则：
      逗号/顿号 -> 0.35s；冒号 -> 0.45s；感叹号 -> 0.50s；句号 -> 0.60s
    句尾（无标点或句号结尾）的停顿由 end_pause 控制（默认 0.60s）。
    """
    tokens = re.split(r"([,，、;；:：!！.。])", text)
    pieces = []
    buf = ""
    for tok in tokens:
        if not tok:
            continue
        if tok in ",，、;；":
            if buf.strip():
                pieces.append((buf.strip(), _PAUSE_COMMA))
            buf = ""
        elif tok in ":：":
            if buf.strip():
                pieces.append((buf.strip(), _PAUSE_COLON))
            buf = ""
        elif tok in "!！":
            if buf.strip():
                pieces.append((buf.strip(), _PAUSE_EXCLAM))
            buf = ""
        elif tok in ".。":
            if buf.strip():
                pieces.append((buf.strip(), end_pause or _PAUSE_PERIOD))
            buf = ""
        else:
            buf += tok
    if buf.strip():
        pieces.append((buf.strip(), end_pause or _PAUSE_PERIOD))
    return pieces


def build_report(fc: dict, forecast_date: datetime.date) -> tuple:
    """返回 (pieces, summary)。pieces = [(text, pause_after_sec), ...]。"""
    day_weather = fc["day_weather"] or "晴"
    night_weather = fc["night_weather"] or day_weather
    high = fc["day_temp"]
    low = fc["night_temp"]
    wind_dir = fc["day_wind_dir"] or fc["night_wind_dir"] or "无"
    if wind_dir != "无" and not wind_dir.endswith("风"):
        wind_dir += "风"
    wind_max = max(fc["day_power_max"], fc["night_power_max"])
    weekday = forecast_date.weekday()

    # 地名：泉州崇武（用户选定发音：泉州 Chôan-chiu，崇武 Tshiông-bú）
    PLACE = "Chôan-chiu Tshiông-bú"
    # 明天（用户指定用"明仔日" bîn-á-ji̍t）
    TOMORROW = "bîn-á-ji̍t"

    date_tailo = (f"{TOMORROW} {_MONTH_TAILO[forecast_date.month]} "
                  f"{num2tailo(forecast_date.day)}-hō, {WEEKDAY_TAILO[weekday]}")

    # 句子列表（先不标点，逐句生成碎片）
    sentences = [
        "Lí hó--ah, huan-gîng siu-thiaⁿ thiⁿ-khì ī-pò.",  # 你好，欢迎收听天气预报。
        f"{date_tailo}, {PLACE} ê thiⁿ-khì:",                  # 明仔日X月X号礼拜X，泉州崇武的天气：
        f"Ji̍t-sî {_weather_tailo(day_weather)}, siong-jua̍h {num2tailo(high)} tōo.",
        f"Àm-sî {_weather_tailo(night_weather)}, kē-un {num2tailo(low)} tōo.",
        f"{WIND_TAILO.get(wind_dir, 'pak-hong')}, {num2tailo(wind_max)} kip.",
    ]
    if _is_rain(day_weather) or _is_rain(night_weather):
        sentences.append(f"{TOMORROW} ē lo̍h-hōo, tshut-mn̂g kì--tit tòa hōo-sòaⁿ.")
    if wind_max >= 5:
        sentences.append("Hái-kîⁿ thàu-hong tsin tuā, saⁿ tshīng kāu--leh, mn̂g-thang kuainn hó.")
    if high >= 33:
        sentences.append("Ji̍t-thâu tsin iām, sió tshut-mn̂g, tsi̍h tsuí.")
    if low <= 12:
        sentences.append("Thiⁿ-khì kuânn, saⁿ ke tsi̍t niá, mài siū-kuânn.")
    sentences.append(f"Hó--ah, {TOMORROW} tshut-mn̂g tsù-ì, pîng-an sūn-suī.")

    pieces = []
    for i, sent in enumerate(sentences):
        end_pause = _ENDING_PAUSE if i == len(sentences) - 1 else None
        pieces.extend(_split_pieces(sent, end_pause=end_pause))

    # 汉字摘要
    rain_txt = "有雨" if (_is_rain(day_weather) or _is_rain(night_weather)) else "无雨"
    weather_txt = day_weather if day_weather == night_weather else f"{day_weather}转{night_weather}"
    summary = (f"{forecast_date.month}月{forecast_date.day}号 {WEEKDAY_CN[weekday]} 泉州崇武："
               f"{weather_txt} {low}~{high}度，"
               f"{wind_dir}{wind_max}级，{rain_txt}")
    return pieces, summary
