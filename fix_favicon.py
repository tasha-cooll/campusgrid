import base64
import os

# Simple gold "CG" favicon as base64 SVG
svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="#0B1120" rx="6"/>
  <text x="16" y="22" font-family="Georgia,serif" font-size="16" font-weight="bold"
        fill="#C9A84C" text-anchor="middle">CG</text>
</svg>"""

os.makedirs('ui/static', exist_ok=True)
with open('ui/static/favicon.svg', 'w') as f:
    f.write(svg)
print('Favicon updated')
