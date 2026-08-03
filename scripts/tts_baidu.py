# -*- coding: utf-8 -*-
"""百度智能云 TTS：大模型音库发音人「度阿闽-闽南男声」per=4132。

免费额度：短文本在线合成，实名认证后送 1 万次测试资源
（每 120 GBK 字节计 1 次，1 分钟闽南语文案约 4~5 次/天，约可用 5~6 年）。
"""
import os
import re
import subprocess
import json
import datetime
import requests

TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
TTS_URL = "https://tsn.baidu.com/text2audio"
PER_MINNAN = "4132"  # 度阿闽-闽南男声（大模型音库）
CUID = "weather-bot"
MAX_GBK_BYTES = 800  # 单段上限 1024，留余量


def get_token(api_key, secret_key):
    r = requests.post(TOKEN_URL, params={
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key,
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"百度 token 获取失败: {data}")
    return data["access_token"]


def _split_text(text):
    """按标点把文本切成 <=800 GBK 字节的段，单段太长时硬切。"""
    parts = []
    cur = ""
    for ch in text:
        cur += ch
        if len(cur.encode("gbk", errors="ignore")) >= MAX_GBK_BYTES:
            parts.append(cur)
            cur = ""
    if cur:
        parts.append(cur)
    return parts


def _synth_one(token, text, per):
    r = requests.post(TTS_URL, data={
        "tex": text, "tok": token, "cuid": CUID, "ctp": 1,
        "lan": "zh", "per": per, "aue": 3, "spd": 4, "pit": 5, "vol": 15,
    }, timeout=60)
    ctype = r.headers.get("Content-Type", "")
    if ctype.startswith("audio/"):
        return r.content
    try:
        err = r.json()
        raise RuntimeError(f"百度 TTS 错误 err_no={err.get('err_no')} msg={err.get('err_msg')}")
    except ValueError:
        raise RuntimeError(f"百度 TTS 非预期响应: {r.text[:200]}")


def _concat_mp3(parts, out_path):
    """优先 ffmpeg 拼接，不可用时二进制直接拼接（mp3 帧可播放）。"""
    try:
        listfile = out_path + ".list"
        with open(listfile, "w", encoding="utf-8") as f:
            for p in parts:
                f.write(f"file '{p}'\n")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
             "-c", "copy", out_path],
            check=True, capture_output=True)
        return
    except Exception:
        with open(out_path, "wb") as f:
            for p in parts:
                f.write(open(p, "rb").read())


def synthesize(text, out_path, api_key=None, secret_key=None):
    """合成 mp3 到 out_path，记录用量台账，返回计费段数。"""
    api_key = api_key or os.environ.get("BAIDU_API_KEY")
    secret_key = secret_key or os.environ.get("BAIDU_SECRET_KEY")
    if not api_key or not secret_key:
        raise RuntimeError("缺少 BAIDU_API_KEY / BAIDU_SECRET_KEY")

    token = get_token(api_key, secret_key)
    chunks = _split_text(text)
    tmp_parts = []
    for i, chunk in enumerate(chunks):
        tmp = f"{out_path}.part{i}.mp3"
        with open(tmp, "wb") as f:
            f.write(_synth_one(token, chunk, PER_MINNAN))
        tmp_parts.append(tmp)
    _concat_mp3(tmp_parts, out_path)
    for p in tmp_parts:
        try:
            os.remove(p)
        except OSError:
            pass

    # 用量台账 site/stats.json
    stats_path = os.path.join(os.path.dirname(out_path), "stats.json")
    stats = []
    if os.path.exists(stats_path):
        try:
            stats = json.load(open(stats_path, encoding="utf-8"))
        except Exception:
            stats = []
    stats.append({
        "date": datetime.date.today().isoformat(),
        "chunks": len(chunks),
        "cost": len(chunks),  # 每段 1 次（120GBK 字节计 1 次，超限由切段控制）
        "total_chunks": sum(s["chunks"] for s in stats) + len(chunks),
    })
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    return len(chunks)
