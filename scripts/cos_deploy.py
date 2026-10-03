# -*- coding: utf-8 -*-
"""把 site/ 部署到腾讯云 CloudBase 静态托管（底层 COS bucket）。

为什么用 COS SDK 而不是 tcb CLI：
- tcb hosting deploy 走美国 GitHub Actions → 腾讯云，2.4MB 音频常超时（19 分钟失败）
- COS SDK put_object 有自动重试/分块上传，且无需 npm install CLI，更快更稳

环境变量：COS_SECRET_ID / COS_SECRET_KEY（CAM 密钥）。
Bucket 与 Region 固定为 CloudBase 静态托管环境 qzmj 的底层存储。
"""
import os
import sys
from qcloud_cos import CosConfig, CosS3Client

SECRET_ID = os.environ["COS_SECRET_ID"]
SECRET_KEY = os.environ["COS_SECRET_KEY"]
# CloudBase 免费体验版 qzmj 环境的静态托管底层 COS bucket（tcb hosting detail 查得）
REGION = "ap-shanghai"
BUCKET = "2eb6-static-qzmj-d8ge0bj5g9257711b-1463592371"


def upload_dir(local_dir, prefix="weather"):
    cfg = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
    cli = CosS3Client(cfg)
    n = 0
    for root, _, files in os.walk(local_dir):
        for name in files:
            if name.endswith(".raw.wav"):
                continue  # TTS 中间文件不上传
            local = os.path.join(root, name)
            rel = os.path.relpath(local, local_dir).replace("\\", "/")
            key = f"{prefix}/{rel}" if prefix else rel
            # 大文件（>1MB，如音频）用分块上传（断点续传，跨境稳定）；小文件直传
            if os.path.getsize(local) > 1024 * 1024:
                cli.upload_file(Bucket=BUCKET, LocalFilePath=local, Key=key,
                                PartSize=1, MAXThread=5, EnableMD5=False)
            else:
                with open(local, "rb") as f:
                    cli.put_object(Bucket=BUCKET, Body=f.read(), Key=key,
                                   ContentType=_content_type(name))
            n += 1
            print(f"  ↑ {key}")
    print(f"上传完成: {n} 个文件")
    return n


def keepalive(days_threshold=0):
    """距仓库最后一次 commit 超过阈值天数时，push 一个空 commit。

    背景（2026-10-03 教训）：GitHub 规定仓库 60 天无 commit 活动会自动禁用
    定时 workflow。改用 COS 直传后每日播报不再产生 commit，仓库活动必须
    由本函数显式维持。仅在 GitHub Actions 环境运行（本地跳过）。

    注意：commit message 必须以 "weather update" 开头 —— daily-weather.yml
    的防循环条件会跳过该类 commit 触发的 push 事件，避免无限递归运行。
    """
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    import subprocess
    import datetime
    last = subprocess.run(["git", "log", "-1", "--format=%cI"],
                         capture_output=True, text=True, check=True).stdout.strip()
    days = (datetime.date.today() - datetime.date.fromisoformat(last.split("T")[0])).days
    if days < days_threshold:
        return
    print(f"距最后 commit 已 {days} 天（阈值 {days_threshold}），push 保活 commit...")
    for args in (
        ["git", "config", "user.name", "weather-bot"],
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        ["git", "commit", "--allow-empty",
         "-m", "weather update keepalive (prevent scheduled workflow auto-disable)"],
        ["git", "push"],
    ):
        subprocess.run(args, check=True)
    print("保活 commit 已推送")


def _content_type(name):
    return {
        ".html": "text/html; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".webmanifest": "application/manifest+json",
    }.get(os.path.splitext(name)[1].lower(), "application/octet-stream")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
    upload_dir(src)
    keepalive()
