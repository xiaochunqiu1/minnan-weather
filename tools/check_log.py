# -*- coding: utf-8 -*-
"""查看最近一次失败的 workflow 日志。

用法：GITHUB_TOKEN=<token> python tools/check_log.py
"""
import json
import gzip
import os
import urllib.request

TOKEN = os.environ["GITHUB_TOKEN"]  # 从环境变量读取，禁止硬编码密钥
BASE = "https://api.github.com/repos/xiaochunqiu1/minnan-weather/actions"


def fetch(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
    })
    return json.load(urllib.request.urlopen(req, timeout=30))


d = fetch(f"{BASE}/runs?per_page=1")
run_id = d["workflow_runs"][0]["id"]
print("run_id:", run_id, d["workflow_runs"][0]["conclusion"])

jobs = fetch(f"{BASE}/runs/{run_id}/jobs")
for j in jobs["jobs"]:
    print(f"job: {j['name']} | {j['status']} {j['conclusion']}")
    for s in j["steps"]:
        print(f"  - {s['name']}: {s['status']} ({s.get('conclusion', '-')})")
    print("== 日志尾部（含错误）==")
    log_url = f"{BASE}/jobs/{j['id']}/logs"
    try:
        req = urllib.request.Request(log_url, headers={"Authorization": f"Bearer {TOKEN}"})
        raw = urllib.request.urlopen(req, timeout=30).read()
        try:
            text = gzip.decompress(raw).decode("utf-8", errors="replace")
        except Exception:
            text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()
        # 打印最后 60 行
        for line in lines[-60:]:
            print(line[:250])
    except Exception as e:
        print("log fetch fail:", e)
