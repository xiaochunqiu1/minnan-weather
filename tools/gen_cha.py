# -*- coding: utf-8 -*-
"""用 cha 读法重新生成台风场景与阴冷场景验证。"""
import sys, datetime
sys.path.insert(0, "scripts")
import copywriter, tts_mms
import soundfile as sf

# 台风场景（十一级）
fc1 = {"day_weather": "暴雨", "night_weather": "大雨", "day_temp": 27, "night_temp": 24,
       "day_wind_dir": "东北风", "night_wind_dir": "东北风", "day_power_max": 10, "night_power_max": 11}
d1 = datetime.date(2026, 8, 7)
pieces, s = copywriter.build_report(fc1, d1)
dur = tts_mms.synthesize(pieces, "chk1.wav")
data, sr = sf.read("chk1.wav")
sf.write("test_台风场景_cha版.mp3", data, sr, format="MP3")
print("台风场景:", s, f"({dur:.1f}s)")
for p in pieces:
    if "kip" in p[0] or "hong" in p[0]:
        print("  风:", p[0])

# 阴冷场景（十一月十五号）
fc2 = {"day_weather": "阴", "night_weather": "多云", "day_temp": 12, "night_temp": 8,
       "day_wind_dir": "北风", "night_wind_dir": "北风", "day_power_max": 4, "night_power_max": 5}
d2 = datetime.date(2026, 11, 15)
pieces, s = copywriter.build_report(fc2, d2)
dur = tts_mms.synthesize(pieces, "chk2.wav")
data, sr = sf.read("chk2.wav")
sf.write("test_阴冷场景_cha版.mp3", data, sr, format="MP3")
print("阴冷场景:", s, f"({dur:.1f}s)")
for p in pieces:
    if "gue̍h" in p[0] or "hō" in p[0]:
        print("  日期:", p[0])
