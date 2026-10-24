# 🌤 景德镇天气可视化项目

这是一个基于 Python 的爬虫与数据可视化项目，用于抓取景德镇市未来 7 天的天气数据，并自动生成交互式的可视化网页。

## 📌 项目功能
- **数据获取**：利用 `requests` 请求天气 API，获取温度、天气状况、湿度、降水量及风力风向数据。
- **数据处理**：将风力文本转数字、WMO 天气代码转中文、角度转风向。
- **数据可视化**：
  - 使用 `matplotlib` 生成温度静态趋势图（PNG）。
  - 使用 `pyecharts` 生成交互式网页图表（温度折线图、湿度与降水双 Y 轴图、风力柱状图）。
- **自动化部署**：通过 `GitHub Actions` 每天定时自动运行脚本，更新数据并发布到 `GitHub Pages`。

## 🛠️ 技术栈
- **语言**：Python 3.12+ (本地使用 3.14)
- **网络请求**：`requests`
- **网页解析**：`BeautifulSoup4` (早期版本使用)
- **可视化**：`matplotlib`、`pyecharts` (ECharts)
- **自动化**：`GitHub Actions`、`GitHub Pages`

## 📂 项目结构
```text
weather_jingdezhen/
├── .github/workflows/
│   └── update_weather.yml   # GitHub Actions 定时任务配置
├── .gitignore               # Git 忽略文件配置
├── main.py                  # 核心爬虫与可视化脚本
├── requirements.txt         # 项目依赖清单
├── weather_report.html      # 生成的可视化网页（由 Actions 自动更新）
└── README.md                # 项目说明文档