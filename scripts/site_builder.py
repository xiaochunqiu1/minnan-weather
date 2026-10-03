# -*- coding: utf-8 -*-
"""渲染播放页 + 写 latest.json（版本二：今天+明天双日结构）。

manifest 结构：
{
  "date": ..., "audio": ..., "summary": ...,   # 顶层兼容字段（指向明天）：
                                               # 旧版播放页只认这些，行为与版本一一致
  "today":     {date, audio, summary},         # 新版播放页 <19 点播这个
  "tomorrow":  {date, audio, summary},         # 新版播放页 ≥19 点播这个
  "updated": ...
}
"""
import json
import os
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(ROOT, "site")
TEMPLATE = os.path.join(ROOT, "templates", "player.html")


def build_days(today_entry, tomorrow_entry):
    os.makedirs(SITE_DIR, exist_ok=True)

    latest = {
        # 顶层兼容字段（=明天），旧版播放页（无 today/tomorrow 逻辑）读顶层照常工作
        "date": tomorrow_entry["date"],
        "audio": tomorrow_entry["audio"],
        "summary": tomorrow_entry["summary"],
        # 新版播放页按北京时间 19 点分界自选
        "today": today_entry,
        "tomorrow": tomorrow_entry,
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    with open(os.path.join(SITE_DIR, "latest.json"), "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)

    # 渲染播放页（页面内容全部由 JS 动态填充，无需模板占位符）
    html = open(TEMPLATE, encoding="utf-8").read()
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.join(SITE_DIR, "index.html")
