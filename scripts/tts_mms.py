# -*- coding: utf-8 -*-
"""Meta MMS-TTS 闽南语合成（台罗拼音输入，本地模型，逐句合成+插静音拼接）。

模型：facebook/mms-tts-nan（CC-BY-NC 4.0，个人非商用免费）
- 输入台罗拼音 Tâi-lô，输出真闽南语语音
- 本地 CPU 推理（GitHub Actions ubuntu runner 可跑）
- 逐句合成、句间插静音，避免长文本节奏失控

模型文件来源（两种方式任选）：
1. 本地目录 models/mms-tts-nan/（手动下载）
2. 首次运行时自动从 HuggingFace 下载（HF_ENDPOINT 可设镜像）
"""
import os
import numpy as np
import scipy.io.wavfile as wavfile
import torch
from transformers import VitsModel, AutoTokenizer

# 模型优先找本地目录，其次在线下载
_LOCAL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "mms-tts-nan")
_REMOTE = "facebook/mms-tts-nan"
SILENCE_SEC = 0.45          # 句间静音时长（秒）
SEED = 42                   # 固定随机种子，保证每次合成节奏一致
WAV_SR = 16000

_model = None
_tokenizer = None


def _load():
    global _model, _tokenizer
    if _model is not None:
        return
    model_dir = _LOCAL_DIR if os.path.exists(os.path.join(_LOCAL_DIR, "model.safetensors")) else _REMOTE
    torch.manual_seed(SEED)
    _model = VitsModel.from_pretrained(model_dir)
    _tokenizer = AutoTokenizer.from_pretrained(model_dir)
    _model.eval()


def _synth_segment(text: str) -> np.ndarray:
    """合成单句，返回 16kHz 单声道 numpy 波形。"""
    inputs = _tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = _model(**inputs).waveform
    return output.squeeze().cpu().numpy()


def synthesize(segments, out_path, sample_rate=WAV_SR):
    """逐碎片合成并拼接（碎片间按标点类型插入停顿），输出 wav。返回总时长秒数。

    segments: 列表，元素为 str 文本 或 (text, pause_after_seconds) 元组。
    """
    _load()
    chunks = []
    for seg in segments:
        if isinstance(seg, tuple):
            text, pause = seg
        else:
            text, pause = seg, SILENCE_SEC
        text = text.strip()
        if not text:
            continue
        wav = _synth_segment(text)
        chunks.append(wav)
        chunks.append(np.zeros(int(sample_rate * pause), dtype=np.float32))
    full = np.concatenate(chunks) if chunks else np.zeros(1, dtype=np.float32)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    # 归一化避免削波
    peak = np.max(np.abs(full))
    if peak > 0.95:
        full = full * (0.95 / peak)
    wavfile.write(out_path, sample_rate, full)
    return len(full) / sample_rate
