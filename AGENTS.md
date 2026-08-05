# AGENTS.md

## 项目
崇武镇闽南语语音天气预报：每天 19:00 自动生成次日闽南语播报并部署到 CloudBase，老人点手机桌面图标收听。

## 怎么跑
```bash
pip install -r requirements.txt
AMAP_KEY=<高德Key> python scripts/main.py   # 生成 site/ 内容（天气→台罗文案→MMS TTS→混音→渲染）
```
云端由 `.github/workflows/daily-weather.yml` 定时跑（UTC 11:00 = 北京 19:00），部署：`tcb hosting deploy ./site /weather -e <TCB_ENV_ID>`。

## 技术栈
Python（高德天气 API + Meta MMS-TTS `facebook/mms-tts-nan` + scipy/soundfile 音频混音）· GitHub Actions · 腾讯云 CloudBase 静态托管（免费体验版）

## 目录约定
- `scripts/`：主流程（main.py 编排；copywriter.py 台罗文案词表；tts_mms.py 真闽南语合成；audio_mix.py 背景乐；site_builder.py 渲染）
- `templates/player.html`：播放页模板（PWA）
- `site/`：部署产物（tcb hosting deploy 推送，不入库音频之外的中间文件）
- `tools/`：一次性工具
- 废弃文件：`scripts/tts_baidu.py`（百度=闽南腔普通话，弃）、`scripts/cos_upload.py`（COS 2024 政策强制下载，弃）

## 当前状态
- ✅ 已上线：https://qzmj-d8ge0bj5g9257711b-1463592371.tcloudbaseapp.com/weather/
- Secrets：AMAP_KEY / TCB_SECRET_ID / TCB_SECRET_KEY / TCB_ENV_ID
- 环境到期 2027-02-05，需免费续期
- 文案发音改 `scripts/copywriter.py` 的台罗词表
