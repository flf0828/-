# ============================================================
# 景德镇未来 7 天天气爬虫 + 可视化
# 数据源：中国天气网 http://www.weather.com.cn/weather/101240801.shtml
# 输出：temperature.png / wind.png / weather_report.html
# ============================================================

import requests
from bs4 import BeautifulSoup
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import rcParams

from pyecharts.charts import Line, Bar
from pyecharts import options as opts


# ------------------------------------------------------------
# 1. 请求 + 解析
# ------------------------------------------------------------
URL = "http://www.weather.com.cn/weather/101240801.shtml"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

resp = requests.get(URL, headers=HEADERS, timeout=15)
resp.encoding = "utf-8"

soup = BeautifulSoup(resp.text, "html.parser")
div_7d = soup.find("div", {"id": "7d"})
if div_7d is None:
    raise SystemExit("❌ 未找到 div#7d，中国天气网页面结构可能变了")

lis = div_7d.find_all("li")

forecast = []
for li in lis[:7]:
    date = li.find("h1").get_text(strip=True)
    weather = li.find("p", class_="wea")["title"]
    high_temp = int(li.find("p", class_="tem").find("span").get_text(strip=True))
    low_temp = int(
        li.find("p", class_="tem").find("i").get_text(strip=True).replace("℃", "")
    )
    wind_span = li.find("p", class_="win").find("em").find("span")
    wind_dir = wind_span["title"] if wind_span else "未知"
    wind_power = li.find("p", class_="win").find("i").get_text(strip=True)

    forecast.append({
        "日期": date,
        "天气": weather,
        "最高温": high_temp,
        "最低温": low_temp,
        "风向": wind_dir,
        "风力": wind_power,
    })

print(f"✅ 已抓取 {len(forecast)} 天数据")

# 提取画图用的平行列表
dates = [d["日期"] for d in forecast]
highs = [d["最高温"] for d in forecast]
lows = [d["最低温"] for d in forecast]


# ------------------------------------------------------------
# 2. 风力文本转数字（"<3级" → 3，"3-4级" → 4）
# ------------------------------------------------------------
def power_to_num(p: str) -> int:
    p = p.replace("级", "").replace("<", "").replace("≤", "")
    if "-" in p:
        p = p.split("-")[-1]
    try:
        return int(p)
    except ValueError:
        return 0


wind_powers = [power_to_num(d["风力"]) for d in forecast]


# ------------------------------------------------------------
# 3. 动态解读文字（根据实际数据生成，不写死）
# ------------------------------------------------------------
high_max, high_min = max(highs), min(highs)
low_max, low_min = max(lows), min(lows)

max_diff_day = max(forecast, key=lambda d: d["最高温"] - d["最低温"])
max_diff = max_diff_day["最高温"] - max_diff_day["最低温"]

temp_note = (
    f"最高温在 {high_min}–{high_max}℃ 之间，最低温在 {low_min}–{low_max}℃ 之间。"
    f"昼夜温差最大的是 {max_diff_day['日期']}（温差 {max_diff}℃），注意增减衣物。"
)

strongest = max(forecast, key=lambda d: power_to_num(d["风力"]))
wind_note = (
    f"未来 7 天风力整体平稳，最大风力出现在 {strongest['日期']}"
    f"（{strongest['风力']}，{strongest['风向']}）。"
)


# ------------------------------------------------------------
# 4. matplotlib 静态图（保存 PNG）
# ------------------------------------------------------------
rcParams["font.sans-serif"] = ["Microsoft YaHei"]
rcParams["axes.unicode_minus"] = False

# 温度折线
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(dates, highs, marker="o", color="tomato", label="最高温")
ax.plot(dates, lows, marker="o", color="deepskyblue", label="最低温")
for x, y in zip(dates, highs):
    ax.annotate(f"{y}℃", (x, y), textcoords="offset points", xytext=(0, 8), ha="center")
for x, y in zip(dates, lows):
    ax.annotate(f"{y}℃", (x, y), textcoords="offset points", xytext=(0, -15), ha="center")
ax.set_title("景德镇未来 7 天温度预报")
ax.set_xlabel("日期")
ax.set_ylabel("温度（℃）")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("temperature.png", dpi=150)
plt.close(fig)

# 风向风力表格
wind_info = [f'{d["风向"]} {d["风力"]}' for d in forecast]
fig2, ax2 = plt.subplots(figsize=(10, 3))
ax2.axis("off")
table = ax2.table(
    cellText=[wind_info],
    colLabels=dates,
    rowLabels=["风向风力"],
    loc="center",
    cellLoc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2)
ax2.set_title("景德镇未来 7 天风向风力")
plt.tight_layout()
plt.savefig("wind.png", dpi=150)
plt.close(fig2)

print("✅ matplotlib 静态图已保存：temperature.png / wind.png")


# ------------------------------------------------------------
# 5. pyecharts 图表（只取 embed 片段，不单独落盘）
# ------------------------------------------------------------
line = (
    Line(init_opts=opts.InitOpts(width="100%", height="420px"))
    .add_xaxis(dates)
    .add_yaxis(
        "最高温", highs, is_smooth=True,
        markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(type_="max", name="最高")]),
    )
    .add_yaxis(
        "最低温", lows, is_smooth=True,
        markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(type_="min", name="最低")]),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="温度趋势"),
        xaxis_opts=opts.AxisOpts(name="日期"),
        yaxis_opts=opts.AxisOpts(name="温度（℃）"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
)

bar = (
    Bar(init_opts=opts.InitOpts(width="100%", height="420px"))
    .add_xaxis(dates)
    .add_yaxis("风力等级", wind_powers)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="风力等级"),
        xaxis_opts=opts.AxisOpts(name="日期"),
        yaxis_opts=opts.AxisOpts(name="风力（级）", max_=6),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
    .set_series_opts(label_opts=opts.LabelOpts(is_show=True, formatter="{c} 级"))
)

line_html = line.render_embed()
bar_html = bar.render_embed()


# ------------------------------------------------------------
# 6. 拼接美化 HTML
# ------------------------------------------------------------
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>景德镇未来 7 天天气可视化</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    background: linear-gradient(135deg, #e0f7fa 0%, #f1f8e9 100%);
    color: #333;
    min-height: 100vh;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 30px 20px; }}
  .header {{ text-align: center; margin-bottom: 30px; }}
  .header h1 {{ font-size: 28px; margin: 0 0 8px; color: #00695c; }}
  .header p {{ color: #607d8b; font-size: 14px; margin: 0; }}
  .card {{
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    padding: 20px;
    margin-bottom: 24px;
  }}
  .card h2 {{
    font-size: 18px;
    color: #00695c;
    margin: 0 0 12px;
    border-left: 4px solid #26a69a;
    padding-left: 10px;
  }}
  .note {{
    font-size: 13px;
    color: #78909c;
    margin-top: 12px;
    line-height: 1.7;
    background: #f5f9f8;
    border-radius: 6px;
    padding: 10px 12px;
  }}
  .footer {{ text-align: center; font-size: 12px; color: #90a4ae; margin-top: 20px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🌤 景德镇未来 7 天天气可视化</h1>
    <p>数据来源：中国天气网 · 生成时间：{now_str}</p>
  </div>

  <div class="card">
    <h2>温度趋势</h2>
    {line_html}
    <div class="note">{temp_note}</div>
  </div>

  <div class="card">
    <h2>风力等级</h2>
    {bar_html}
    <div class="note">{wind_note}</div>
  </div>

  <div class="footer">本页面由 Python 爬虫 + pyecharts 自动生成 · 重新运行脚本即可更新数据</div>
</div>
</body>
</html>
"""

with open("weather_report.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ 已生成合并美化版：weather_report.html")