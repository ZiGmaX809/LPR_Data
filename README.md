# LPR 数据自动采集工具

## 📊 项目简介

本项目是一个自动采集中国银行 LPR（贷款市场报价利率）数据的工具，支持定时抓取最新数据并保存为多种格式，便于数据分析和使用。

## ✨ 主要功能

- 🔄 自动抓取中国银行官网最新 LPR 数据
- 📅 每日定时更新（北京时间上午10点）
- 📁 支持多种数据格式：
  - `LPR_Data.txt` - 原始文本格式
  - `LPR_Data.json` - JSON 格式，便于程序处理
  - `LPR_Data.csv` - CSV 格式，便于表格软件查看
- 🤖 GitHub Actions 自动化运行
- 📦 自动生成数据备份

## 🚀 快速开始

### 本地运行

1. **克隆仓库**
```bash
git clone https://github.com/ZiGmaX809/LPR_Data.git
cd LPR_Data
```

2. **安装依赖**
```bash
pip install requests beautifulsoup4
```

3. **运行脚本**
```bash
# 检查数据并更新（如果需要）
python lpr_scraper.py

# 强制更新数据
python lpr_scraper.py --force
```

### 自动化运行

项目已配置 GitHub Actions 工作流，会：
- 每天北京时间上午10点自动运行
- 检测到新数据时自动提交到仓库
- 生成数据备份到 Artifacts

## 📋 数据格式

### JSON 格式示例
```json
{
  "last_updated": "2025-08-12T00:41:26.123456",
  "data": [
    {
      "date": "2024-08-20",
      "one_year_rate": "3.35",
      "five_year_rate": "3.85"
    }
  ]
}
```

### CSV 格式示例
```csv
日期,一年期LPR(%),五年期以上LPR(%)
2024-08-20,3.35,3.85
2024-07-22,3.35,3.85
```

## 🛠️ 技术栈

- **Python 3.9+** - 主要开发语言
- **requests** - HTTP 请求库
- **BeautifulSoup4** - HTML 解析库
- **GitHub Actions** - 自动化工具

## 📁 文件说明

- `lpr_scraper.py` - 主要爬虫脚本
- `.github/workflows/update-lpr-data.yml` - GitHub Actions 工作流配置
- `LPR_Data.txt` - 原始文本格式数据
- `LPR_Data.json` - JSON 格式数据
- `LPR_Data.csv` - CSV 格式数据

## ⚙️ 配置说明

### GitHub Actions 权限
确保仓库的 Actions 具有以下权限：
- `contents: write` - 用于提交数据文件
- `actions: read` - 用于读取工作流

### 手动触发
可以在 GitHub 仓库的 Actions 页面手动触发工作流运行。

## 📊 数据来源

数据来源：[中国银行官网 - 人民币存贷款基准利率](https://www.bankofchina.com/fimarkets/lilv/fd32/201310/t20131031_2591219.html)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目基于 MIT 许可证开源。

## 📞 联系方式

如有问题或建议，请通过 GitHub Issues 联系。

---

**更新频率**: 每日自动更新  
**最后更新**: 通过 GitHub Actions 自动维护