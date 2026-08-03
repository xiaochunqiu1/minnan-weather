# -*- coding: utf-8 -*-
"""渲染播放页 + 写 latest.json。"""
import json
import os
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(ROOT, "site")
TEMPLATE = os.path.join(ROOT, "templates", "player.html")


def build(summary: str, forecast_date: datetime.date, audio_file: str):
    os.makedirs(SITE_DIR, exist_ok=True)

    # latest.json（带页面显示日期）
    latest = {
        "date": forecast_date.isoformat(),
        "audio": audio_file,          # 相对 site/ 的路径，如 audio/2026-08-04.mp3
        "summary": summary,
        "updated": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    with open(os.path.join(SITE_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)

    # 渲染播放页
    html = open(TEMPLATE, encoding="utf-8").read()
    html = html.replace("{{DATE_CN}}", summary.split("崇武")[0].strip())
    html = html.replace("{{SUMMARY}}", summary)
    html = html.replace("{{AUDIO}}", audio_file)
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.join(SITE_DIR, "index.html")
