# AGENTS.md

## 项目
崇武镇闽南语语音天气预报：每天 19:00 自动生成次日闽南语播报并部署到 CloudBase，老人点手机桌面图标收听。

## 怎么跑
```bash
pip install -r requirements.txt
AMAP_KEY=<高德Key> python scripts/main.py   # 生成 site/ 内容（天气→台罗文案→MMS TTS→混音→渲染）
```
云端由 `.github/workflows/daily-weather.yml` 定时跑（UTC 11:00 = 北京 19:00）：
1. main.py 生成 wav → 2. workflow 用 ffmpeg 压成 mp3（~316KB）→ 3. `python scripts/cos_deploy.py site/` 用 COS SDK 分块上传（跨境稳定）。

## 技术栈
Python（高德天气 API + Meta MMS-TTS `facebook/mms-tts-nan` + scipy/soundfile 音频混音）· GitHub Actions · 腾讯云 CloudBase 静态托管（免费体验版，底层 COS bucket）

## 目录约定
- `scripts/`：主流程（main.py 编排；copywriter.py 台罗文案词表；tts_mms.py 真闽南语合成；audio_mix.py 背景乐；cos_deploy.py COS SDK 部署；site_builder.py 渲染）
- `templates/player.html`：播放页模板（PWA）
- `site/`：部署产物（cos_deploy.py 推送；音频为 mp3，不入库）
- `tools/`：一次性工具（check_log.py 的 token 必须从环境变量 GITHUB_TOKEN 读，禁止硬编码）

## 当前状态
- ✅ 已上线：https://qzmj-d8ge0bj5g9257711b-1463592371.tcloudbaseapp.com/weather/
- GitHub 仓库：`xiaochunqiu1/minnan-weather`（已从旧名 `-` 改名，旧链接自动跳转）
- Secrets：AMAP_KEY / TCB_SECRET_ID / TCB_SECRET_KEY / TCB_ENV_ID（COS_SECRET_ID/KEY 复用 TCB_* 值）
- 环境到期 2027-02-05，需免费续期
- 文案发音改 `scripts/copywriter.py` 的台罗词表；嘱咐语已结合天气（雨天带伞/晴天日头/阴天热/冷添衣/风大防风）
- **约定（用户 2026-08-05 明确）**：GitHub token 不重建、不轮换（用户接受现状）；如遇到 push protection 拦截，说明代码含密钥，先清密钥再推送，不要反复建议用户重建 token
- **推送技巧**：本机 `credential.helper=helper-selector` 会导致 `git push` 无输出失败，需 `git -c credential.helper= push <完整URL> main:main`
- **推送兜底（2026-10-03 验证）**：git 通道故障（本地代理 502 / 直连超时）时，用 gh CLI 走 Contents API 直传文件（api.github.com 可直连）：`gh api --method PUT repos/xiaochunqiu1/minnan-weather/contents/<路径> -f message="..." -f sha=<GET 拿到的当前 sha> -f content="$(base64 -w0 <文件>)"`；注意本机环境变量里的代理（HTTPS_PROXY=127.0.0.1:xxxx）会让 gh 也失败，命令前要清空 `HTTPS_PROXY= HTTP_PROXY= https_proxy= http_proxy=`
- **keepalive 保活（2026-10-03 加）**：GitHub 规定仓库 60 天无 commit 会自动禁用定时 workflow；COS 直传部署不产生 commit，故 `cos_deploy.py` 的 keepalive() 在每次 Actions 部署后检查距最后 commit 天数，≥45 天自动 push 空 commit（message 以 "weather update" 开头，复用 daily-weather.yml 防循环条件；push 失败只警告不报错，下次运行自动重试）。端到端已验证（run 37097533628/37097685514）
- **本机 git 凭据 scope 限制**：本机所有凭据（GCM OAuth / gh token）都无 `workflow` 权限，**不能 push 涉及 `.github/workflows/` 文件改动的 commit**（会报 "refusing to allow an OAuth App..."）；改 workflow 文件需用户在网页 UI 操作或换有 workflow scope 的 token
