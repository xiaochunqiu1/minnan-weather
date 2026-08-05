# 崇武镇闽南语语音天气预报

每天北京时间 19:00 自动生成次日闽南语天气预报，老人晚 8 点后点手机桌面「天气」图标 → 点大喇叭即可收听。全程零费用、零日常人工操作、纯云端运行（电脑无需开机）。

## 在线地址（现役）

https://qzmj-d8ge0bj5g9257711b-1463592371.tcloudbaseapp.com/weather/

- 托管：腾讯云 CloudBase 免费体验版静态托管（部署在 `/weather` 子路径，复用 qzmj 环境，不覆盖原项目）
- 环境到期 2027-02-05，到期在控制台免费续期
- PWA 支持：手机浏览器打开后「添加到主屏幕」，桌面出现太阳云朵图标，全屏独立打开

## 架构

```
GitHub Actions (cron UTC 11:00 = 北京 19:00)
  → 高德天气 API 取惠安县次日预报
  → 生成台罗拼音分段文案（scripts/copywriter.py）
  → Meta MMS-TTS 闽南语模型合成语音（facebook/mms-tts-nan，本地 CPU）
  → 程序合成钢琴琶音背景乐 + 混音（scripts/audio_mix.py）
  → 渲染 site/index.html + latest.json（scripts/site_builder.py）
  → tcb hosting deploy ./site /weather → CloudBase 静态托管
```

## Secrets（GitHub 仓库 Actions）

| Secret | 说明 |
|---|---|
| `AMAP_KEY` | 高德 Web 服务 Key（天气数据） |
| `TCB_SECRET_ID` | 腾讯云 CAM API 密钥 SecretId |
| `TCB_SECRET_KEY` | 腾讯云 CAM API 密钥 SecretKey |
| `TCB_ENV_ID` | CloudBase 环境 ID（`qzmj-d8ge0bj5g9257711b`） |

## 本地开发

```bash
pip install -r requirements.txt
# 需要先 export AMAP_KEY
python scripts/main.py
# 部署（可选）：
# npm i -g @cloudbase/cli && tcb login --apiKeyId <SecretId> --apiKey <SecretKey>
# tcb hosting deploy ./site /weather -e <TCB_ENV_ID>
```

## 调整文案

所有闽南语发音集中在 `scripts/copywriter.py`（台罗词表 + 标点碎片化），想改某个词直接改对应台罗拼音。生成音频在 `site/audio/`。

## 项目结构

```
.github/workflows/daily-weather.yml   # 定时任务（UTC 11:00 = 北京 19:00）+ push 触发 + 防循环
scripts/
  main.py                             # 主流程编排
  weather.py                          # 高德天气 API
  copywriter.py                       # 台罗拼音文案（词表 + 标点级停顿）
  tts_mms.py                          # Meta MMS-TTS 本地推理（真闽南语）
  audio_mix.py                        # 钢琴琶音背景乐合成 + 混音
  site_builder.py                     # 渲染播放页 + latest.json
  tts_baidu.py                        # [废弃] 百度 TTS（度阿闽=闽南腔普通话，已弃用）
templates/player.html                 # 播放页模板（PWA + SW）
site/                                 # CloudBase 部署目录（tcb hosting deploy 推送）
  index.html (生成)
  manifest.webmanifest                # PWA 桌面图标
  sw.js                               # Service Worker
  icon.png                            # 太阳+云朵图标
  latest.json (生成)
  audio/YYYY-MM-DD.wav (生成)
tools/                                # 一次性工具（图标生成、调试等）
```

## 故障告警

云端任务任一步失败 → GitHub 自动邮件通知仓库主（Settings → Notifications 确认）。

## 方案历史（为什么是现在这套）

- 百度方言发音人（度阿闽/度小台/台媒女声）= 普通话+腔调，不是真闽南语 → 弃
- EdgeOne Pages = 默认域名 3 小时过期 → 弃
- 腾讯云 COS 静态托管 = 2024 政策新桶默认域名强制下载（需备案域名）→ 弃
- **CloudBase 免费体验版 = 唯一满足 零费用+国内快+浏览器正常渲染+永久域名 的方案** → 现役
