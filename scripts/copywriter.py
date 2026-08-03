# -*- coding: utf-8 -*-
"""闽南语播报文案模板。

集中在这里方便家人试听后代为调整。文案用闽南语口语习惯的汉字书写，
由百度 TTS「度阿闽」以闽南语发音。数字一律转汉字读法，避免念阿拉伯数字。

百度 TTS 支持注音语法：词(拼音) 可纠正发音，如 崇(chong2)武，按需使用。
"""
import datetime

# ---- 数字转汉字（0~99）----
_CN = "零一二三四五六七八九"
_UNIT = ["", "十", "百"]


def num2cn(n: int) -> str:
    n = int(n)
    if n < 0:
        return "零下" + num2cn(-n)
    if n < 10:
        return _CN[n]
    if n < 100:
        s = _CN[n // 10] + "十" if n // 10 != 1 else "十"
        if n % 10:
            s += _CN[n % 10]
        return s
    if n < 1000:
        s = _CN[n // 100] + "百"
        rest = n % 100
        if rest:
            if rest < 10:
                s += "零" + _CN[rest]
            else:
                s += num2cn(rest)
        return s
    return str(n)


WEEKDAY_CN = ["礼拜一", "礼拜二", "礼拜三", "礼拜四", "礼拜五", "礼拜六", "礼拜日"]

# 判定"会落雨"的天气现象词
_RAIN_WORDS = ("雨", "阵雨", "雷雨", "雷阵雨", "冰雹")


def _is_rain(w: str) -> bool:
    return any(k in w for k in _RAIN_WORDS)


def build_report(fc: dict, forecast_date: datetime.date) -> tuple:
    """返回 (播报文案, 文字摘要)。"""

    # 日期表述：8月4号，礼拜二
    month_cn = num2cn(forecast_date.month)
    day_cn = num2cn(forecast_date.day)
    date_text = f"{month_cn}月{day_cn}号"
    weekday = WEEKDAY_CN[forecast_date.weekday()]

    day_weather = fc["day_weather"] or "无风无雨"
    night_weather = fc["night_weather"] or day_weather
    high = fc["day_temp"]
    low = fc["night_temp"]
    wind_dir = fc["day_wind_dir"] or fc["night_wind_dir"] or "无"
    wind_max = max(fc["day_power_max"], fc["night_power_max"])

    # 条件分支提醒
    tips = []
    if wind_max >= 5:
        tips.append("海沿透风真大，衫穿厚咧，门窗关好。")
    if _is_rain(day_weather) or _is_rain(night_weather):
        tips.append("明仔载会落雨，出门记的带雨伞。")
    if high >= 33:
        tips.append("日头真炎，少出门，多喝水。")
    if low <= 12:
        tips.append("天气寒，衫加一件，莫受寒。")

    lines = [
        "喂，阿伯，天气报告来咯。",
        f"明仔载{date_text}，{weekday}，崇武的天气：",
        f"日时{day_weather}，高温{num2cn(high)}度；",
        f"暗时{night_weather}，低温{num2cn(low)}度。",
        f"{wind_dir}，{num2cn(wind_max)}级。",
    ]
    lines += tips
    lines.append("好啦，明仔载出门注意，平安顺遂。")
    text = "".join(lines)

    # 文字摘要（页面大字/子女核对用）
    rain_txt = "有雨" if (_is_rain(day_weather) or _is_rain(night_weather)) else "无雨"
    summary = (f"{forecast_date.month}月{forecast_date.day}号 {weekday} 崇武："
               f"{day_weather}转{night_weather} {low}~{high}度，"
               f"{wind_dir}{wind_max}级，{rain_txt}")
    return text, summary
