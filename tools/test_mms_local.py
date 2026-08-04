# -*- coding: utf-8 -*-
"""用本地模型文件合成台罗拼音的闽南语语音（不依赖在线下载）。"""
import torch
from transformers import VitsModel, AutoTokenizer
import scipy.io.wavfile as wavfile

MODEL_DIR = "D:/WorkBuddy任务空间/任务空间/0-小项目/天气预报/models/mms-tts-nan"

print("从本地加载模型 ...")
model = VitsModel.from_pretrained(MODEL_DIR)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
print("加载完成, 采样率:", model.config.sampling_rate)

# 台罗拼音文本（闽南语）—— 天气播报样例
texts = {
    "test1": "Lí hó, a-peh, thiⁿ-khì pò-tō lâi--lo̍h. Bîn-á-tsài, tshîng-bú ê thiⁿ-khì: tsá-sî tsîng, koân-un saⁿ-tsa̍p-sì tōo; àm-sî tsîng, kē-un jī-tsa̍p-la̍k tōo. Pak-hong, saⁿ kip. Lí hó, bîn-á-tsài tshut-mn̂g tsù-ì, pîng-an sūn-suī.",
    "test2": "Bîn-á-tsài beh lo̍h-hōo, tshut-mn̂g kì--tit tòa hōo-sòaⁿ.",
}

for name, text in texts.items():
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    wav = output.squeeze().cpu().numpy()
    fname = f"D:/WorkBuddy任务空间/任务空间/0-小项目/天气预报/test_{name}.wav"
    wavfile.write(fname, rate=model.config.sampling_rate, data=wav)
    print(f"已生成 {fname}: 时长 {len(wav)/model.config.sampling_rate:.1f}s")

print("DONE")
