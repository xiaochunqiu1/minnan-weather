# -*- coding: utf-8 -*-
"""生成 PWA 桌面图标：蓝底圆角方块 + 太阳 + 云朵（天气元素，无喇叭）。"""
from PIL import Image, ImageDraw
import math

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 圆角背景（蓝→浅蓝渐变）
def rounded(draw, box, r, fill):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=r, fill=fill)

top = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
dt = ImageDraw.Draw(top)
for i in range(SIZE):
    t = i / SIZE
    r = int(122 + (190 - 122) * t)
    g = int(192 + (232 - 192) * t)
    b = int(245 + (250 - 245) * t)
    dt.line([(0, i), (SIZE, i)], fill=(r, g, b, 255))

mask = Image.new("L", (SIZE, SIZE), 0)
dm = ImageDraw.Draw(mask)
dm.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=112, fill=255)
img.paste(top, (0, 0), mask)
d = ImageDraw.Draw(img)

# 太阳（右上）：光晕 + 圆
sun_cx, sun_cy, sun_r = 372, 150, 82
d.ellipse([sun_cx - sun_r - 22, sun_cy - sun_r - 22, sun_cx + sun_r + 22, sun_cy + sun_r + 22], fill=(255, 214, 110, 120))
d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=(255, 196, 46, 255))

# 云朵（左下）：三圆 + 底座
def cloud(cx, cy, scale=1.0, alpha=255):
    col = (255, 255, 255, alpha)
    d.ellipse([cx - 60 * scale, cy - 40 * scale, cx + 60 * scale, cy + 60 * scale], fill=col)
    d.ellipse([cx - 110 * scale, cy - 10 * scale, cx + 10 * scale, cy + 90 * scale], fill=col)
    d.ellipse([cx - 30 * scale, cy - 60 * scale, cx + 90 * scale, cy + 40 * scale], fill=col)
    d.rounded_rectangle([cx - 130 * scale, cy, cx + 110 * scale, cy + 42 * scale], radius=20, fill=col)

cloud(150, 340, 1.0, 255)
# 小云点缀
cloud(80, 130, 0.45, 190)

img.save("D:/WorkBuddy任务空间/任务空间/0-小项目/天气预报/site/icon.png")
print("icon.png saved")
