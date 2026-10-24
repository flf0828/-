# ============================================================
# 景德镇未来 7 天天气爬虫 + 可视化 (Open-Meteo 版)
# 数据源：https://open-meteo.com/
# 输出：temperature.png / wind.png / weather_report.html
# ============================================================

import requests
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import rcParams

from pyecharts.charts import Line, Bar, Grid
from pyecharts import options as opts


# ------------------------------------------------------------
# 1. 请求 + 解析（Open-Meteo 版）
# ------------------------------------------------------------
URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": 29.27,
    "longitude": 117.18,
    "daily": [
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "relative_humidity_2m_max",
        "precipitation_sum",
        "wind_speed_10m_max",
        "wind_direction_10m_dominant",
    ],
    "timezone": "Asia/Shanghai",
    "forecast_days": 7,
}

resp = requests.get(URL, params=params, timeout=15)
resp.raise_for_status()
data = resp.json()["daily"]

# WMO 天气代码映射
WMO_CODES = {
    0: "晴", 1: "多云", 2: "多云", 3: "阴",
    45: "雾", 48: "雾凇",
    51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 81: "阵雨", 82: "强阵雨",
    95: "雷阵雨", 96: "雷阵雨", 99: "雷阵雨",
}

forecast = []
weekday_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
dirs = ["北风", "东北风", "东风", "东南风", "南风", "西南风", "西风", "西北风"]

for i in range(7):
    # 日期解析
    dt = datetime.strptime(data["time"][i], "%Y-%m-%d")
    date_label = f"{dt.month}月{dt.day}日（{weekday_map[dt.weekday()]}）"

    # 风向、风速转风力
    deg = data["wind_direction_10m_dominant"][i]
    wind_dir = dirs[round(deg / 45) % 8]
    speed = data["wind_speed_10m_max"][i]
    if speed < 1:    power = "0级"
    elif speed < 6:  power = "1级"
    elif speed < 12: power = "2级"
    elif speed < 20: power = "3级"
    elif speed < 29: power = "4级"
    elif speed < 39: power = "5级"
    else:            power = "6级+"

    forecast.append({
        "日期": date_label,
        "天气": WMO_CODES.get(data["weather_code"][i], "未知"),
        "最高温": round(data["temperature_2m_max"][i]),
        "最低温": round(data["temperature_2m_min"][i]),
        "风向": wind_dir,
        "风力": power,
        "湿度": round(data["relative_humidity_2m_max"][i]),
        "降水量": round(data["precipitation_sum"][i], 1),
    })

print(f"✅ 已抓取 {len(forecast)} 天数据")

# 提取画图用的平行列表
dates = [d["日期"] for d in forecast]
highs = [d["最高温"] for d in forecast]
lows = [d["最低温"] for d in forecast]
humidity = [d["湿度"] for d in forecast]
precip = [d["降水量"] for d in forecast]


# ------------------------------------------------------------
# 2. 风力文本转数字
# ------------------------------------------------------------
def power_to_num(p: str) -> int:
    p = p.replace("级", "").replace("+", "")
    try:
        return int(p)
    except ValueError:
        return 0

wind_powers = [power_to_num(d["风力"]) for d in forecast]


# ------------------------------------------------------------
# 3. 动态解读文字
# ------------------------------------------------------------
high_max, high_min = max(highs), min(highs)
low_max, low_min = min(lows), min(lows)
max_diff_day = max(forecast, key=lambda d: d["最高温"] - d["最低温"])
max_diff = max_diff_day["最高温"] - max_diff_day["最低温"]

temp_note = (
    f"最高温在 {high_min}–{high_max}℃ 之间，最低温在 {low_min}–{low_max}℃ 之间。"
    f"昼夜温差最大的是 {max_diff_day['日期']}（温差 {max_diff}℃），注意增减衣物。"
)

max_rain = max(forecast, key=lambda d: d["降水量"])
max_hum = max(forecast, key=lambda d: d["湿度"])
climate_note = (
    f"未来 7 天最大相对湿度为 {max_hum['湿度']}%（{max_hum['日期']}），"
    f"预计降水量最多的一天是 {max_rain['日期']}（{max_rain['降水量']} mm）。"
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

print("✅ matplotlib 静态图已保存：temperature.png")


# ------------------------------------------------------------
# 5. pyecharts 图表
# ------------------------------------------------------------
# 温度折线
line = (
    Line(init_opts=opts.InitOpts(width="100%", height="350px"))
    .add_xaxis(dates)
    .add_yaxis("最高温", highs, is_smooth=True,
               markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max", name="最高")]))
    .add_yaxis("最低温", lows, is_smooth=True,
               markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="min", name="最低")]))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="温度趋势"),
        xaxis_opts=opts.AxisOpts(name="日期"),
        yaxis_opts=opts.AxisOpts(name="温度（℃）"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
)

# 降水 + 湿度双 Y 轴
bar_rain = (
    Bar(init_opts=opts.InitOpts(width="100%", height="350px"))
    .add_xaxis(dates)
    .add_yaxis("降水量 (mm)", precip, yaxis_index=0, color="#3398DB")
    .extend_axis(
        yaxis=opts.AxisOpts(name="湿度 (%)", type_="value", min_=0, max_=100)
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="湿度与降水量"),
        xaxis_opts=opts.AxisOpts(name="日期"),
        yaxis_opts=opts.AxisOpts(name="降水量 (mm)", min_=0),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
    )
)
line_hum = (
    Line()
    .add_xaxis(dates)
    .add_yaxis("相对湿度 (%)", humidity, yaxis_index=1, is_smooth=True, color="#FF7F50")
)
bar_rain.overlap(line_hum)

# 风力柱状
bar_wind = (
    Bar(init_opts=opts.InitOpts(width="100%", height="350px"))
    .add_xaxis(dates)
    .add_yaxis("风力等级", wind_powers, color="#26a69a")
    .set_global_opts(
        title_opts=opts.TitleOpts(title="风力等级"),
        xaxis_opts=opts.AxisOpts(name="日期"),
        yaxis_opts=opts.AxisOpts(name="风力（级）", max_=6),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    )
    .set_series_opts(label_opts=opts.LabelOpts(is_show=True, formatter="{c} 级"))
)

line_html = line.render_embed()
bar_rain_html = bar_rain.render_embed()
bar_wind_html = bar_wind.render_embed()


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
    margin: 0; font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    background: linear-gradient(135deg, #e0f7fa 0%, #f1f8e9 100%);
    color: #333; min-height: 100vh;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 30px 20px; }}
  .header {{ text-align: center; margin-bottom: 30px; }}
  .header h1 {{ font-size: 28px; margin: 0 0 8px; color: #00695c; }}
  .header p {{ color: #607d8b; font-size: 14px; margin: 0; }}
  .card {{
    background: #fff; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    padding: 20px; margin-bottom: 24px;
  }}
  .card h2 {{
    font-size: 18px; color: #00695c; margin: 0 0 12px;
    border-left: 4px solid #26a69a; padding-left: 10px;
  }}
  .note {{
    font-size: 13px; color: #78909c; margin-top: 12px; line-height: 1.7;
    background: #f5f9f8; border-radius: 6px; padding: 10px 12px;
  }}
  .footer {{ text-align: center; font-size: 12px; color: #90a4ae; margin-top: 20px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🌤 景德镇未来 7 天天气可视化</h1>
    <p>数据来源：Open-Meteo · 生成时间：{now_str}</p>
  </div>

  <div class="card">
    <h2>温度趋势与天气状况</h2>
    {line_html}
    <div class="note">{temp_note}</div>
    <div class="note" style="margin-top:5px;">每日天气：{ "，".join([f"{d['日期']} {d['天气']}" for d in forecast]) }</div>
  </div>

  <div class="card">
    <h2>湿度与降水量</h2>
    {bar_rain_html}
    <div class="note">{climate_note}</div>
  </div>

  <div class="card">
    <h2>风力等级</h2>
    {bar_wind_html}
  </div>

  <div class="footer">本页面由 Python 爬虫 + pyecharts 自动生成 · 重新运行脚本即可更新数据</div>
</div>
</body>
</html>
"""

with open("weather_report.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("✅ 已生成合并美化版：weather_report.html")