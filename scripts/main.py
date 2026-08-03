# -*- coding: utf-8 -*-
"""主流程：明天天气 → 闽南语文案 → 百度TTS → 渲染播放页。

任何异常向上抛出（非零退出码），GitHub Actions 会标记失败并邮件告警。
"""
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import weather as weather_mod       # noqa: E402
import copywriter                   # noqa: E402
import tts_baidu                    # noqa: E402
import site_builder                 # noqa: E402

BEIJING_TZ = datetime.timezone(datetime.timedelta(hours=8))


def main():
    # 1. 计算"明天"（北京时间，无夏令时，固定 +8）
    tomorrow = datetime.datetime.now(BEIJING_TZ).date() + datetime.timedelta(days=1)
    print(f"[1/4] 预报日期: {tomorrow}")

    # 2. 天气
    fc = weather_mod.get_forecast(tomorrow.isoformat())
    print(f"[2/4] 天气: {fc}")

    # 3. 文案
    text, summary = copywriter.build_report(fc, tomorrow)
    print(f"[3/4] 文案: {text}")
    print(f"      摘要: {summary}")

    # 4. TTS
    audio_dir = os.path.join(site_builder.SITE_DIR, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    mp3 = os.path.join(audio_dir, f"{tomorrow.isoformat()}.mp3")
    chunks = tts_baidu.synthesize(text, mp3)
    print(f"[4/4] 音频: {mp3} (计费段数 {chunks})")
    if not os.path.exists(mp3) or os.path.getsize(mp3) < 1000:
        raise RuntimeError("生成的 mp3 异常（文件过小）")

    # 5. 渲染站点
    site_builder.build(summary, tomorrow, f"audio/{tomorrow.isoformat()}.mp3")
    print("完成。")

    # 预览文案与摘要（Actions 日志可见）
    print("=" * 40)
    print(summary)
    print(text)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
