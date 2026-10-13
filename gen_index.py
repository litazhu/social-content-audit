#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫描目录中的 xlsx，生成静态索引页 index.html"""
import os, html, datetime

BASE = os.path.dirname(os.path.abspath(__file__))

GROUPS = [
    (
        "竞品对标批次 · 个护科技 5 品牌",
        "2026-10 抓取 · 窗口 2025-10-12 ~ 2026-10-12 · 每份 10 个 sheet（含基准对比 / 归因 / Top-Bottom 30% / 结论）",
        ["Dyson", "Laifen", "Oura", "Mendi", "Ocjoy"],
    ),
    (
        "口腔护理 8 品牌 · 多平台审计",
        "2026-09 抓取 · 覆盖 Instagram / YouTube / Facebook / TikTok 等平台",
        ["BURST_OralCare", "EMS_Dental", "Fairywill", "Goby", "OralB_Social",
         "PhilipsSonicare_Social", "quip", "usmile"],
    ),
    (
        "单平台专项审计（早期批次）",
        "Instagram / YouTube 单一平台深度审计",
        ["OralB_Instagram", "PhilipsSonicare_Instagram", "Waterpik_YouTube"],
    ),
]

def human(n):
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} MB"
    return f"{n / 1024:.0f} KB"

def title_of(fn):
    stem = fn[:-5]
    pretty = stem.replace("_", " ").replace("Social Content Audit", "社媒内容审计")
    pretty = pretty.replace("Instagram Content Audit", "Instagram 审计")
    pretty = pretty.replace("YouTube Content Audit FILLED", "YouTube 审计")
    pretty = pretty.replace(" EN", "（英文原版）")
    return pretty

def main():
    files = sorted(f for f in os.listdir(BASE) if f.lower().endswith(".xlsx"))
    cards_by_group = []
    used = set()

    for gname, gdesc, keys in GROUPS:
        rows = []
        for f in files:
            if f in used:
                continue
            stem = f[:-5]
            if any(stem.startswith(k.rstrip("_")) or stem == k or k in stem for k in keys):
                pass
            # 精确匹配：stem 以 key 开头，或 stem 去掉 _EN 后等于 key
            base = stem[:-3] if stem.endswith("_EN") else stem
            hit = any(base.startswith(k) for k in keys)
            if hit:
                rows.append(f)
                used.add(f)
        rows.sort()
        if rows:
            cards_by_group.append((gname, gdesc, rows))

    leftover = [f for f in files if f not in used]
    if leftover:
        cards_by_group.append(("其他文件", "", leftover))

    total_size = sum(os.path.getsize(os.path.join(BASE, f)) for f in files)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    parts = []
    parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>社媒内容审计工作簿 · 下载中心</title>
<style>
  :root {{
    --bg:#f6f7f9; --card:#ffffff; --line:#e3e6ea; --text:#1d2129;
    --muted:#6b7280; --accent:#2563eb; --accent-soft:#eff4ff; --tag:#f0f2f5;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,sans-serif;
    line-height:1.6; }}
  .wrap {{ max-width:960px; margin:0 auto; padding:40px 20px 64px; }}
  header {{ margin-bottom:28px; }}
  h1 {{ font-size:26px; margin:0 0 8px; letter-spacing:-.3px; }}
  .sub {{ color:var(--muted); font-size:14px; }}
  .meta {{ margin-top:14px; display:flex; gap:8px; flex-wrap:wrap; }}
  .pill {{ background:var(--tag); color:var(--muted); font-size:12px;
    padding:4px 10px; border-radius:999px; }}
  h2 {{ font-size:17px; margin:34px 0 4px; }}
  .gdesc {{ color:var(--muted); font-size:13px; margin:0 0 14px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(290px,1fr)); gap:12px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
    padding:14px 16px; display:flex; flex-direction:column; gap:8px;
    transition:box-shadow .15s, border-color .15s; }}
  .card:hover {{ box-shadow:0 4px 14px rgba(0,0,0,.07); border-color:#c9d2e0; }}
  .card .name {{ font-size:14px; font-weight:600; word-break:break-all; }}
  .card .foot {{ display:flex; justify-content:space-between; align-items:center;
    font-size:12px; color:var(--muted); }}
  .btn {{ display:inline-block; background:var(--accent-soft); color:var(--accent);
    border:none; text-decoration:none; font-size:12px; font-weight:600;
    padding:6px 12px; border-radius:8px; }}
  .btn:hover {{ background:#dbe6ff; }}
  footer {{ margin-top:44px; padding-top:18px; border-top:1px solid var(--line);
    color:var(--muted); font-size:12px; }}
  code {{ background:var(--tag); padding:1px 6px; border-radius:4px; font-size:12px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>社媒内容审计工作簿 · 下载中心</h1>
    <div class="sub">每个品牌一份 .xlsx，含 10 个 sheet：概况 / 分平台明细 / 基准对比 / Top-Bottom 30% / 归因分析 / 发布节奏 / 结论建议 / 编码规则。</div>
    <div class="meta">
      <span class="pill">{len(files)} 份工作簿</span>
      <span class="pill">合计 {human(total_size)}</span>
      <span class="pill">更新于 {now}</span>
    </div>
  </header>
""")

    for gname, gdesc, rows in cards_by_group:
        parts.append(f"  <h2>{html.escape(gname)}</h2>\n")
        if gdesc:
            parts.append(f'  <p class="gdesc">{html.escape(gdesc)}</p>\n')
        parts.append('  <div class="grid">\n')
        for f in rows:
            size = human(os.path.getsize(os.path.join(BASE, f)))
            parts.append(
                f'    <div class="card">\n'
                f'      <div class="name">{html.escape(title_of(f))}</div>\n'
                f'      <div class="foot"><span>{html.escape(f)} · {size}</span>'
                f'<a class="btn" href="./{html.escape(f)}" download>下载</a></div>\n'
                f'    </div>\n'
            )
        parts.append("  </div>\n")

    parts.append(f"""
  <footer>
    直接点击「下载」即可获取 .xlsx；也可以复制文件名的原始地址
    <code>https://github.com/litazhu/social-content-audit/raw/main/&lt;文件名&gt;</code> 用于分享或脚本下载。
  </footer>
</div>
</body>
</html>
""")

    out = "".join(parts)
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8") as fp:
        fp.write(out)
    print("wrote index.html, files:", len(files), "used:", len(used))

if __name__ == "__main__":
    main()
