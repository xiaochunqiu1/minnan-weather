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
            with open(local, "rb") as f:
                cli.put_object(Bucket=BUCKET, Body=f.read(), Key=key,
                               ContentType=_content_type(name))
            n += 1
            print(f"  ↑ {key}")
    print(f"上传完成: {n} 个文件")
    return n


def _content_type(name):
    return {
        ".html": "text/html; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".wav": "audio/wav",
        ".webmanifest": "application/manifest+json",
    }.get(os.path.splitext(name)[1].lower(), "application/octet-stream")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
    upload_dir(src)
