# -*- coding: utf-8 -*-
"""主流程：今天+明天两天天气 → 台罗分段文案 → Meta MMS 闽南语 TTS → 混音 → 渲染播放页。

播放策略（版本二，2026-10-03 用户确认）：
云端同时存今天/明天两份音频，播放页按北京时间 19 点分界自选——
19 点前播今天（老人白天听当天的），19 点后播明天（老人晚上 20 点听次日的）。
任务无论几点跑（GitHub cron 延迟常态 3~10 小时），生成的都是"当天+次日"，
与运行时刻无关，天然免疫调度延迟。

任何异常向上抛出（非零退出码），GitHub Actions 会标记失败并邮件告警。
"""
import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import weather as weather_mod       # noqa: E402
import copywriter                   # noqa: E402
import tts_mms                      # noqa: E402
import audio_mix                    # noqa: E402
import site_builder                 # noqa: E402

BEIJING_TZ = datetime.timezone(datetime.timedelta(hours=8))


def build_day(day):
    """生成单日播报：天气 → 文案 → TTS → 混音。返回摘要文本。"""
    fc = weather_mod.get_forecast(day.isoformat())
    print(f"  天气: {fc}")
    segments, summary = copywriter.build_report(fc, day)
    print(f"  台罗分段: {len(segments)} 段 | 摘要: {summary}")
    wav_dir = os.path.join(site_builder.SITE_DIR, "audio")
    os.makedirs(wav_dir, exist_ok=True)
    raw_path = os.path.join(wav_dir, f"{day.isoformat()}.raw.wav")
    dur = tts_mms.synthesize(segments, raw_path)
    print(f"  语音合成: {day} (时长 {dur:.1f}s)")
    if not os.path.exists(raw_path) or os.path.getsize(raw_path) < 10000:
        raise RuntimeError(f"生成的 wav 异常（{day} 文件过小）")
    wav_path = os.path.join(wav_dir, f"{day.isoformat()}.wav")
    dur_mixed = audio_mix.mix(raw_path, wav_path)
    print(f"  混音完成: {wav_path} (时长 {dur_mixed:.1f}s)")
    try:
        os.remove(raw_path)  # 清理中间文件（失败不影响主流程）
    except OSError:
        pass
    return summary


def main():
    today = datetime.datetime.now(BEIJING_TZ).date()
    tomorrow = today + datetime.timedelta(days=1)
    print(f"[1/3] 生成今天 {today} 的播报")
    summary_today = build_day(today)
    print(f"[2/3] 生成明天 {tomorrow} 的播报")
    summary_tomorrow = build_day(tomorrow)
    print("[3/3] 渲染站点")
    # manifest 直接引用 .mp3：云端 workflow 的 Compress 步骤会把 wav 转成同名 mp3，
    # 其 latest.json 改写（.wav→.mp3 替换）对新结构是无操作，无需改 workflow
    site_builder.build_days(
        {"date": today.isoformat(), "audio": f"audio/{today.isoformat()}.mp3",
         "summary": summary_today},
        {"date": tomorrow.isoformat(), "audio": f"audio/{tomorrow.isoformat()}.mp3",
         "summary": summary_tomorrow},
    )
    print("完成。")
    print("=" * 40)
    print(f"今天: {summary_today}")
    print(f"明天: {summary_tomorrow}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
