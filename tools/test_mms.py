# -*- coding: utf-8 -*-
"""测试 Meta MMS-TTS 闽南语模型（输入台罗拼音）。"""
import torch
from transformers import VitsModel, AutoTokenizer
import scipy.io.wavfile as wavfile

print("加载模型 facebook/mms-tts-nan ...")
model = VitsModel.from_pretrained("facebook/mms-tts-nan")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-nan")
print("模型加载完成, 采样率:", model.config.sampling_rate)

# 台罗拼音测试文本（闽南语）
texts = [
    "Lí hó, a-peh, thiⁿ-khì pò-tō lâi--lo̍h.",
    "Bîn-á-tsài tshîng-bú ê thiⁿ-khì: tsá-sî tsîng, koân-un saⁿ-tsa̍p-sì tōo.",
]
for i, text in enumerate(texts):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    wav = output.squeeze().cpu().numpy()
    fname = f"test_mms_{i}.wav"
    wavfile.write(fname, rate=model.config.sampling_rate, data=wav)
    print(f"已生成 {fname}: {wav.shape}")

print("DONE")
