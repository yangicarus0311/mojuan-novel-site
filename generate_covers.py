#!/usr/bin/env python3
"""为墨卷9部作品生成SVG封面图，存入 covers 目录"""

import os

COVERS_DIR = "/Users/agentbaby/.openclaw/workspace/novel-site/frontend/public/covers"
os.makedirs(COVERS_DIR, exist_ok=True)

covers = [
    {
        "id": 1, "title": "苍穹之上", "author": "云中客",
        "gradient": ["#0a1628", "#1a2a5e"], "icon": "☁️",
        "style": "主题: 修仙者在云海之上御剑飞行"
    },
    {
        "id": 2, "title": "九天神帝", "author": "忘川风",
        "gradient": ["#1a0a28", "#3a1a5e"], "icon": "👑",
        "style": "金色王冠与九重天"
    },
    {
        "id": 3, "title": "末世手记", "author": "荒原狼",
        "gradient": ["#1a1a1a", "#3a2a1a"], "icon": "💀",
        "style": "废土风格的避难所"
    },
    {
        "id": 4, "title": "长安夜雨", "author": "青衫烟雨",
        "gradient": ["#0a1428", "#2a3050"], "icon": "🌧️",
        "style": "雨夜长安城的古建筑"
    },
    {
        "id": 5, "title": "我在异界开客栈", "author": "逍遥散人",
        "gradient": ["#2a1a0a", "#5a3a1a"], "icon": "🏮",
        "style": "古风客栈，灯笼高挂"
    },
    {
        "id": 6, "title": "朝暮不相见", "author": "半夏微凉",
        "gradient": ["#2a0a28", "#5a1a40"], "icon": "🌸",
        "style": "花瓣飘落与两个背影"
    },
    {
        "id": 7, "title": "深海囚笼", "author": "暗夜行者",
        "gradient": ["#0a1a2a", "#0a3a3a"], "icon": "🔱",
        "style": "深海中的铁笼与光"
    },
    {
        "id": 8, "title": "算法之魂", "author": "量子猫咪",
        "gradient": ["#0a2a1a", "#0a4a3a"], "icon": "🧠",
        "style": "数字矩阵与大脑"
    },
    {
        "id": 9, "title": "青云劫", "author": "夜无痕",
        "gradient": ["#1a1a2a", "#2a3a5a"], "icon": "⚔️",
        "style": "两把剑交叉，青烟缭绕"
    },
]

for c in covers:
    g1, g2 = c["gradient"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 400 560">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#{g1}" />
      <stop offset="100%" style="stop-color:#{g2}" />
    </linearGradient>
    <linearGradient id="overlay" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:rgba(0,0,0,0);stop-opacity:0" />
      <stop offset="100%" style="stop-color:rgba(0,0,0,0.6);stop-opacity:0.6" />
    </linearGradient>
  </defs>
  <!-- Background -->
  <rect width="400" height="560" fill="url(#bg)" rx="12"/>

  <!-- Decorative circles -->
  <circle cx="320" cy="80" r="120" fill="rgba(255,255,255,0.03)" />
  <circle cx="50" cy="460" r="80" fill="rgba(255,255,255,0.02)" />

  <!-- Icon -->
  <text x="200" y="200" text-anchor="middle" font-size="72">{c["icon"]}</text>

  <!-- Title -->
  <text x="200" y="350" text-anchor="middle" font-family="serif" font-size="36" font-weight="bold" fill="#e8e4dc" letter-spacing="4">{c["title"]}</text>

  <!-- Decorative line -->
  <line x1="120" y1="370" x2="280" y2="370" stroke="rgba(201,169,110,0.5)" stroke-width="1" />

  <!-- Author -->
  <text x="200" y="400" text-anchor="middle" font-family="sans-serif" font-size="16" fill="rgba(201,169,110,0.7)" letter-spacing="2">{c["author"]}</text>

  <!-- Bottom category bar -->
  <rect x="0" y="520" width="400" height="40" fill="rgba(0,0,0,0.3)" rx="0" />
  <text x="200" y="545" text-anchor="middle" font-family="sans-serif" font-size="12" fill="rgba(255,255,255,0.4)">墨卷 · 沉浸式阅读</text>
</svg>'''
    path = os.path.join(COVERS_DIR, f"cover-{c['id']}.svg")
    with open(path, "w") as f:
        f.write(svg)
    print(f"✅ 已生成: {path}")

print(f"\n🎉 共生成 {len(covers)} 张封面")
