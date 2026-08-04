# -*- coding: utf-8 -*-
"""清理工作区所有实验音频和临时文件。"""
import os
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 根目录下的所有 wav/mp3/临时 html
for pattern in ["*.wav", "*.mp3", "freepd_home.html", "hf_meta.json", "*.json"]:
    for f in glob.glob(os.path.join(BASE, pattern)):
        if "site/" in f or ".workbuddy" in f:
            continue
        os.remove(f)
        print("删:", os.path.basename(f))

print("清理完成")
