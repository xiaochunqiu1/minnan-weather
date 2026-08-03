# -*- coding: utf-8 -*-
"""本地冒烟测试：用 mock 数据跑 copywriter + site_builder，验证文案和页面渲染。
   不需要任何 API key。"""
import datetime
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import copywriter
import site_builder

# mock 明天天气
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
mock_fc = {
    "date": tomorrow.isoformat(),
    "day_weather": "多云",
    "night_weather": "阵雨",
    "day_temp": 30,
    "night_temp": 24,
    "day_wind_dir": "东北风",
    "night_wind_dir": "东北风",
    "day_power_max": 5,
    "night_power_max": 6,
}

text, summary = copywriter.build_report(mock_fc, tomorrow)
print("=== 播报文案 ===")
print(text)
print()
print("=== 文字摘要 ===")
print(summary)
print()

# 模拟一个 fake 音频占位
fake_mp3 = f"site/audio/{tomorrow.isoformat()}.mp3"
os.makedirs(os.path.dirname(fake_mp3), exist_ok=True)
# 写一个最小的有效 mp3 头占位（仅用于本地渲染验证）
with open(fake_mp3, "wb") as f:
    f.write(b"ID3" + b"\x03" + b"\x00" * 7 + b"\x00" * 4)

out = site_builder.build(summary, tomorrow, f"audio/{tomorrow.isoformat()}.mp3")
print(f"=== 渲染完成: {out} ===")

# 移除假 mp3，避免被 commit
try:
    os.remove(fake_mp3)
except OSError:
    pass
# latest.json / index.html 保留供查看
print("OK")