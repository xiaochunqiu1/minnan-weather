# 崇武镇闽南语语音天气预报

每天北京时间 19:00 自动生成次日闽南语天气预报，老人晚 8 点后点击手机桌面「天气」图标 → 点大喇叭即可收听。零费用、零日常人工操作。

## 一次注册（约半天）

### 1. GitHub 注册与建仓库
1. 访问 https://github.com 注册账号
2. 右上角「+」→「New repository」→ 名称如 `minnan-weather` → 选 Public（私有也可）→ 不勾 README → Create
3. 把本仓库代码 push 到该 GitHub 仓库

### 2. EdgeOne Pages 绑定（固定链接 + PWA 托管）
1. 访问 https://edgeone.ai/ → 用 GitHub 登录
2. Pages → 「Import a project」→ 选刚才建的仓库
3. 输出目录填 `site`，记下分配的域名 `xxx.edgeone.app`
4. 先手动 push 一次 `site/index.html` 占位文件，验证 EdgeOne 能自动部署（URL 直接打开看到页面）

### 3. 百度智能云：获取 TTS 闽南语发音人
> **关键步骤**：必须当天先试调一次接口，确认「度阿闽」在免费额度内。
1. 访问 https://cloud.baidu.com → 注册 → 个人实名认证
2. 控制台 → 短文本在线合成 → **免费测试资源**领取 → **确认额度覆盖大模型音库**
3. 创建应用（语音技术）→ 拿到 **API Key** 和 **Secret Key**

### 4. 高德开放平台：获取天气 Key
1. 访问 https://lbs.amap.com → 注册个人开发者
2. 应用管理 → 创建新应用 → 类型「Web 服务」→ 拿到 **Key**

### 5. 仓库 Secrets 配置
仓库页面 → Settings → Secrets and variables → Actions → New repository secret：
| Secret 名 | 值 |
|---|---|
| `BAIDU_API_KEY` | 百度 API Key |
| `BAIDU_SECRET_KEY` | 百度 Secret Key |
| `AMAP_KEY` | 高德 Key |

### 6. 老人手机配置
1. 浏览器（建议系统自带浏览器）打开 `https://xxx.edgeone.app/`
2. 点击浏览器底部「分享/...」→「添加到主屏幕」
3. 桌面上会出现「天气」图标（太阳+云朵图案）
4. 教老人两步：**点桌面图标 → 点屏幕中间的大喇叭**

## 故障告警
云端任务任一步失败 → GitHub 自动邮件通知仓库主（默认开启，Settings → Notifications 确认）。

## 本地开发
```bash
pip install -r requirements.txt
# 需要先 export 三个 Key
python scripts/main.py
```

## 调整文案
所有闽南语文案集中在 `scripts/copywriter.py`，会闽南语的家人可反复试听 `site/audio/` 下生成的 mp3，按需微调模板。

## 项目结构
```
.github/workflows/daily-weather.yml   # 定时任务（UTC 11:00 = 北京 19:00）
scripts/
  main.py                              # 主流程编排
  weather.py                           # 高德天气
  copywriter.py                        # 闽南语文案模板
  tts_baidu.py                         # 百度 TTS 度阿闽
  site_builder.py                      # 渲染播放页
templates/player.html                  # 播放页模板
site/                                  # EdgeOne 部署目录
  index.html (生成)
  manifest.webmanifest                 # PWA 桌面图标
  sw.js                                # Service Worker
  icon.png                             # 太阳+云朵图标
  latest.json (生成)
  audio/YYYY-MM-DD.mp3 (生成)
  stats.json (生成, 用量台账)
tools/make_icon.py                     # 图标生成脚本
```trigger push 120947
