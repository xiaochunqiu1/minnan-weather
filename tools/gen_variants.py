# -*- coding: utf-8 -*-
"""生成两个搭配版本的完整播报对比。"""
import sys, datetime
sys.path.insert(0, "scripts")
import copywriter, tts_mms
import soundfile as sf

tomorrow = datetime.date(2026, 8, 5)
fc = {
    "date": "2026-08-05", "day_weather": "多云", "night_weather": "阵雨",
    "day_temp": 30, "night_temp": 24,
    "day_wind_dir": "东北风", "night_wind_dir": "东北风",
    "day_power_max": 5, "night_power_max": 6,
}

# ---- 版本 A：v6 当前搭配 ----
pieces, _ = copywriter.build_report(fc, tomorrow)
dur = tts_mms.synthesize(pieces, "vA.wav")
data, sr = sf.read("vA.wav")
sf.write("test_搭配A.mp3", data, sr, format="MP3")
print(f"A 完成 {dur:.1f}s")

# ---- 版本 B：另一组搭配 ----
piecesB, _ = copywriter.build_report(fc, tomorrow)
for i, p in enumerate(piecesB):
    t = p[0]
    t = t.replace("Lí hó--ah, huan-gîng siu-thiaⁿ", "Lí hó, huan-gîng siu-thiann")
    for old, new in [
        ("lé-pài-it", "pài-it"), ("lé-pài-jī", "pài-jī"), ("lé-pài-sann", "pài-sann"),
        ("lé-pài-sù", "pài-sù"), ("lé-pài-gōo", "pài-gōo"),
        ("lé-pài-la̍k", "pài-la̍k"), ("lé-pài-ji̍t", "pài-ji̍t"),
    ]:
        t = t.replace(old, new)
    t = t.replace("siong-jua̍h", "jua̍h")
    t = t.replace("Chôan-chiu Tshiông-bú", "Tsûan-tsiu Tsiông-bú")
    piecesB[i] = (t, p[1])
print("=== B 碎片 ===")
for p in piecesB:
    print("  ", p[0])
dur = tts_mms.synthesize(piecesB, "vB.wav")
data, sr = sf.read("vB.wav")
sf.write("test_搭配B.mp3", data, sr, format="MP3")
print(f"B 完成 {dur:.1f}s")
