# -*- coding: utf-8 -*-
"""天气数据获取：高德地图天气 API（区县级，免费 30 万次/天）。

崇武镇属惠安县，adcode=350521。
"""
import os
import requests

AMAP_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
ADCODE = "350521"  # 惠安县


def _num(s):
    """'≤3' / '4' / '3-4' -> 最大风力数字，用于阈值判断。"""
    import re
    nums = [int(x) for x in re.findall(r"\d+", str(s))]
    return max(nums) if nums else 0


def get_forecast(tomorrow_date, key=None):
    """返回明天的预报 dict：
    {date, day_weather, night_weather, day_temp, night_temp,
     day_wind_dir, night_wind_dir, day_power_max, night_power_max}
    """
    key = key or os.environ.get("AMAP_KEY")
    if not key:
        raise RuntimeError("缺少 AMAP_KEY")
    r = requests.get(AMAP_URL, params={
        "key": key, "city": ADCODE, "extensions": "all",
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "1":
        raise RuntimeError(f"高德天气接口错误: {data.get('info')}")
    casts = data["forecasts"][0]["casts"]
    cast = next((c for c in casts if c["date"] == tomorrow_date), None)
    if cast is None:
        # 兜底：取数组第二项（惯例为明天）
        cast = casts[1] if len(casts) > 1 else casts[0]
    return {
        "date": cast["date"],
        "day_weather": cast.get("dayweather", ""),
        "night_weather": cast.get("nightweather", ""),
        "day_temp": int(float(cast.get("daytemp", 0) or 0)),
        "night_temp": int(float(cast.get("nighttemp", 0) or 0)),
        "day_wind_dir": cast.get("daywind", ""),
        "night_wind_dir": cast.get("nightwind", ""),
        "day_power_max": _num(cast.get("daypower", "0")),
        "night_power_max": _num(cast.get("nightpower", "0")),
    }
