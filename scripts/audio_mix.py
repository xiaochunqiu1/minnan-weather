# -*- coding: utf-8 -*-
"""背景乐合成 + 语音混音。

背景乐：程序合成轻柔钢琴琶音（C-Am-F-G 和弦进行），完全自主生成、无版权问题。
混音策略（用户指定 v2）：
  - 播报过程中背景乐极轻（0.05），不打扰语音
  - 语音结束后背景乐快速渐强（约 1 秒升到 0.55），
  - 纯音乐延续 TAIL_SEC 秒，最后 3 秒渐弱到无声结束
"""
import numpy as np
import scipy.io.wavfile as wavfile

SR = 16000
BGM_SOFT = 0.05      # 播报中背景乐音量（极轻）
BGM_LOUD = 0.55      # 结尾纯音乐最大音量
RISE_SEC = 1.0       # 语音结束后渐强到最大音量的时长
TAIL_SEC = 8.0       # 语音结束后纯音乐延续时长
FADE_SEC = 3.0       # 结尾渐弱时长

# 音符频率（C4=261.63）
NOTE_FREQ = {
    "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00,
    "A3": 220.00, "B3": 246.94,
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00,
    "A4": 440.00, "B4": 493.88, "C5": 523.25, "E5": 659.26, "G5": 783.99,
}
# 柔和和弦进行：C - Am - F - G（每和弦 2 秒）
CHORDS = [
    ["C4", "E4", "G4", "C5"],
    ["A3", "C4", "E4", "A4"],
    ["F3", "A3", "C4", "F4"],
    ["G3", "B3", "D4", "G4"],
]
CHORD_SEC = 2.0
NOTE_EVERY = 0.5   # 琶音间隔


def _note_wave(freq, dur, amp=0.32):
    """钢琴感音符：基频+谐波，指数衰减包络。"""
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    w = (np.sin(2 * np.pi * freq * t)
         + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
         + 0.25 * np.sin(2 * np.pi * freq * 3 * t)
         + 0.1 * np.sin(2 * np.pi * freq * 4 * t))
    env = np.exp(-t * 2.6) * (1 - np.exp(-t * 220))
    return amp * w * env


def synth_piano_bgm(duration: float) -> np.ndarray:
    """生成轻柔钢琴琶音背景，长度>=duration秒。"""
    total = int((duration + CHORD_SEC) * SR)
    bgm = np.zeros(total, dtype=np.float32)
    pos = 0
    idx = 0
    while pos < total:
        chord = CHORDS[idx % len(CHORDS)]
        idx += 1
        for note in chord:
            if pos >= total:
                break
            wav = _note_wave(NOTE_FREQ[note], CHORD_SEC, amp=0.30)
            end = min(pos + len(wav), total)
            bgm[pos:end] += wav[:end - pos]
            pos += int(NOTE_EVERY * SR)
    return bgm[:total]


def _envelope(voice_len: int, total_len: int) -> np.ndarray:
    """背景乐音量包络：播报中极轻 → 语音结束后渐强 → 保持 → 渐弱。

    voice_len: 语音样本数；total_len: 总样本数（含尾部纯音乐）。
    """
    env = np.full(total_len, BGM_SOFT, dtype=np.float32)
    rise_n = int(RISE_SEC * SR)
    fade_n = int(FADE_SEC * SR)
    # 语音结束点开始渐强
    env[voice_len:voice_len + rise_n] = np.linspace(BGM_SOFT, BGM_LOUD, rise_n, dtype=np.float32)
    env[voice_len + rise_n:] = BGM_LOUD
    # 结尾渐弱
    env[-fade_n:] = np.linspace(BGM_LOUD, 0.0, fade_n, dtype=np.float32)
    return env


def mix(voice_path: str, out_path: str, bgm_path: str = None):
    """读语音 wav → 合成背景乐 → 按包络混音 → 输出 wav。

    输出总时长 = 语音时长 + TAIL_SEC（语音结束后背景乐延续）。
    bgm_path 若提供则从文件读取背景乐（wav，须为16k单声道），否则程序合成。
    """
    sr, voice = wavfile.read(voice_path)
    if voice.dtype != np.float32:
        voice = voice.astype(np.float32) / 32768.0
    if voice.ndim > 1:
        voice = voice.mean(axis=1)
    voice_len = len(voice)
    total_len = voice_len + int(TAIL_SEC * sr)

    if bgm_path:
        bsr, bgm = wavfile.read(bgm_path)
        if bgm.dtype != np.float32:
            bgm = bgm.astype(np.float32) / 32768.0
        if bgm.ndim > 1:
            bgm = bgm.mean(axis=1)
        if bsr != sr:
            x = np.linspace(0, len(bgm) - 1, int(len(bgm) * sr / bsr))
            bgm = np.interp(x, np.arange(len(bgm)), bgm)
        if len(bgm) < total_len:
            reps = int(np.ceil(total_len / max(len(bgm), 1))) + 1
            bgm = np.tile(bgm, reps)
        bgm = bgm[:total_len]
        bgm = bgm / (np.max(np.abs(bgm)) + 1e-9)
    else:
        bgm = synth_piano_bgm(total_len / sr)[:total_len]
        bgm = bgm / (np.max(np.abs(bgm)) + 1e-9)

    env = _envelope(voice_len, total_len)
    mixed = np.zeros(total_len, dtype=np.float32)
    mixed[:voice_len] += voice
    mixed += bgm * env
    peak = np.max(np.abs(mixed))
    if peak > 0.97:
        mixed = mixed * (0.97 / peak)

    import os
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wavfile.write(out_path, sr, mixed.astype(np.float32))
    return len(mixed) / sr
