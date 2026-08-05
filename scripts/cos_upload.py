# -*- coding: utf-8 -*-
"""将 site/ 整个目录上传到腾讯云 COS 静态网站托管。"""
import os
import sys
from qcloud_cos import CosConfig, CosS3Client

SECRET_ID = os.environ["COS_SECRET_ID"]
SECRET_KEY = os.environ["COS_SECRET_KEY"]
REGION = os.environ.get("COS_REGION", "ap-guangzhou")
BUCKET = os.environ["COS_BUCKET"]


def upload_dir(local_dir, prefix=""):
    cfg = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
    cli = CosS3Client(cfg)
    n = 0
    for root, _, files in os.walk(local_dir):
        for name in files:
            local = os.path.join(root, name)
            rel = os.path.relpath(local, local_dir).replace("\\", "/")
            key = (prefix + rel) if prefix else rel
            if name.endswith(".raw.wav"):
                continue  # 中间文件不上传
            with open(local, "rb") as f:
                cli.put_object(
                    Bucket=BUCKET,
                    Body=f.read(),
                    Key=key,
                    ContentType=_content_type(name),
                )
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
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
    upload_dir(src)