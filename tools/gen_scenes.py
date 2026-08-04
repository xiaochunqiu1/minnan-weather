# -*- coding: utf-8 -*-
"""生成四个典型天气场景的完整播报，验证内容搭配。"""
import sys, datetime
sys.path.insert(0, "scripts")
import copywriter, tts_mms
import soundfile as sf

scenarios = [
    # 场景1：8月6号 礼拜四 雷阵雨 + 大风（雨+防风+高温提醒全触发）
    ("场景1_雷阵雨大风", datetime.date(2026, 8, 6), {
        "day_weather": "雷阵雨", "night_weather": "雷阵雨",
        "day_temp": 33, "night_temp": 25,
        "day_wind_dir": "西南风", "night_wind_dir": "西南风",
        "day_power_max": 6, "night_power_max": 7,
    }),
    # 场景2：8月7号 礼拜五 台风暴雨（沿海台风天）
    ("场景2_台风暴雨", datetime.date(2026, 8, 7), {
        "day_weather": "暴雨", "night_weather": "大雨",
        "day_temp": 27, "night_temp": 24,
        "day_wind_dir": "东北风", "night_wind_dir": "东北风",
        "day_power_max": 10, "night_power_max": 11,
    }),
    # 场景3：8月8号 礼拜六 晴热（防暑提醒）
    ("场景3_晴热", datetime.date(2026, 8, 8), {
        "day_weather": "晴", "night_weather": "晴",
        "day_temp": 35, "night_temp": 27,
        "day_wind_dir": "东南风", "night_wind_dir": "东南风",
        "day_power_max": 3, "night_power_max": 4,
    }),
    # 场景4：11月15号 礼拜日 阴冷（添衣提醒）
    ("场景4_阴冷添衣", datetime.date(2026, 11, 15), {
        "day_weather": "阴", "night_weather": "多云",
        "day_temp": 12, "night_temp": 8,
        "day_wind_dir": "北风", "night_wind_dir": "北风",
        "day_power_max": 4, "night_power_max": 5,
    }),
]

for name, date, fc in scenarios:
    fc = dict(fc); fc["date"] = date.isoformat()
    pieces, summary = copywriter.build_report(fc, date)
    print(f"===== {name} =====")
    print("摘要:", summary)
    for p in pieces:
        print("  ", p[0])
    dur = tts_mms.synthesize(pieces, f"scene_{name}.wav")
    data, sr = sf.read(f"scene_{name}.wav")
    sf.write(f"test_{name}.mp3", data, sr, format="MP3")
    print(f"  -> 时长 {dur:.1f}s")
    print()
