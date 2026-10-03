# -*- coding: utf-8 -*-
"""主流程：明天天气 → 台罗分段文案 → Meta MMS 闽南语 TTS → 渲染播放页。

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


def main():
    # 1. 计算预报日期（北京时间，固定 +8）
    # 规则：按"北京时间 19 点分界"判断，不依赖任务实际几点跑 ——
    #   19 点前跑（白天手动补跑 / cron 延迟到凌晨前的场景）→ 生成当天预报，
    #   保证老人白天听到的是"今天"；19 点及以后（含 GitHub cron 延迟到
    #   凌晨 0-2 点的补跑，那时仍算"前一天 19 点后"）→ 生成次日预报。
    # 背景：GitHub Actions 共享调度器高峰期常延迟数小时，cron '0 11 * * *'
    #   实测多次拖到北京凌晨才跑，旧的"无条件今天+1"会多跳一天。
    now_bj = datetime.datetime.now(BEIJING_TZ)
    target_date = now_bj.date() if now_bj.hour < 19 else now_bj.date() + datetime.timedelta(days=1)
    print(f"[1/4] 预报日期: {target_date}（当前北京时间 {now_bj.strftime('%H:%M')}）")

    # 2. 天气
    fc = weather_mod.get_forecast(target_date.isoformat())
    print(f"[2/4] 天气: {fc}")

    # 3. 文案（台罗分段）
    segments, summary = copywriter.build_report(fc, target_date)
    print(f"[3/4] 台罗分段:")
    for s in segments:
        print(f"      - {s}")
    print(f"      摘要: {summary}")

    # 4. TTS（Meta MMS 本地模型，输出 wav）
    wav_dir = os.path.join(site_builder.SITE_DIR, "audio")
    os.makedirs(wav_dir, exist_ok=True)
    raw_path = os.path.join(wav_dir, f"{target_date.isoformat()}.raw.wav")
    dur = tts_mms.synthesize(segments, raw_path)
    print(f"[4/5] 语音合成: {raw_path} (时长 {dur:.1f}s)")
    if not os.path.exists(raw_path) or os.path.getsize(raw_path) < 10000:
        raise RuntimeError("生成的 wav 异常（文件过小）")

    # 5. 混入背景乐（轻声 → 结尾渐强 → 渐弱收尾）
    wav_path = os.path.join(wav_dir, f"{target_date.isoformat()}.wav")
    dur_mixed = audio_mix.mix(raw_path, wav_path)
    print(f"[5/5] 混音完成: {wav_path} (时长 {dur_mixed:.1f}s)")
    try:
        os.remove(raw_path)  # 清理中间文件（失败不影响主流程）
    except OSError:
        pass

    # 6. 渲染站点（latest.json 指向 wav；云端 workflow 会再转 mp3 并改写引用）
    site_builder.build(summary, target_date, f"audio/{target_date.isoformat()}.wav")
    print("完成。")
    print("=" * 40)
    print(summary)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
