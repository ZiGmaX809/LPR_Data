# LPR数据完整使用指南

本项目提供了完整的LPR（贷款市场报价利率）数据爬取、分割和管理解决方案，包括自动化工具和GitHub Actions workflows。

## 📋 项目概览

### 核心功能
- 🕷️ **自动爬取**: 定时从银行官网获取最新LPR数据
- ✂️ **数据分割**: 按年份智能分割数据，支持增量导出
- 🔄 **自动化**: GitHub Actions workflows自动化处理
- 📊 **质量监控**: 数据完整性检查和质量报告
- 📦 **多格式支持**: CSV、JSON、TXT三种格式

## 📁 项目文件结构

```
LPR_Data/
├── README.md                       # 项目主说明文档
├── README_完整使用指南.md          # 本完整使用指南
├── LPR_Data.csv                    # 完整的LPR数据（CSV格式）
├── LPR_Data.json                   # 完整的LPR数据（JSON格式）
├── LPR_Data.txt                    # 原始格式数据
├── lpr_scraper.py                  # 基础爬取工具（简单模式）
├── lpr_scraper_integrated.py       # 集成爬取工具（推荐使用）
├── .github/
│   └── workflows/
│       ├── update-lpr-data.yml     # 主数据更新workflow
│       ├── split-lpr-data.yml      # 数据分割workflow
│       └── data-quality-check.yml  # 数据质量检查workflow
└── yearly_data/                    # 按年份分割的数据目录
    ├── LPR_Data_2019.csv          # 2019年数据
    ├── LPR_Data_2019.json
    ├── LPR_Data_2020.csv
    ├── LPR_Data_2020.json
    ├── LPR_Data_2021.csv
    ├── LPR_Data_2021.json
    ├── LPR_Data_2022.csv
    ├── LPR_Data_2022.json
    ├── LPR_Data_2023.csv
    ├── LPR_Data_2023.json
    ├── LPR_Data_2024.csv
    ├── LPR_Data_2024.json
    ├── LPR_Data_2025.csv
    └── LPR_Data_2025.json
```

## 🚀 快速开始

### 本地使用

**推荐方式 - 使用集成工具：**

1. **智能增量更新（推荐）**
```bash
python3 lpr_scraper_integrated.py
```

2. **强制更新所有数据**
```bash
python3 lpr_scraper_integrated.py --force
```

**传统方式 - 仅爬取（不分割）：**

```bash
python3 lpr_scraper.py
```
> 注意：此方式只生成完整数据文件，不按年份分割

### GitHub Actions 自动化

项目配置了完整的自动化 workflows，会自动处理数据更新和分割。

## 🛠️ 工具详细说明

### 1. LPR数据集成爬取工具 (`lpr_scraper_integrated.py`) - ⭐ 推荐使用

#### 功能特性
- 🌐 从中国银行官网自动爬取LPR数据
- ✂️ **集成数据分割**: 爬取时直接按年份分割，无需额外步骤
- 🔄 **智能增量更新**: 自动比较新旧数据，只更新有变化的年份
- 📅 自动检测数据是否需要更新
- 💾 支持多种输出格式（CSV、JSON、TXT）
- ⚡ **高效处理**: 一次运行完成爬取和分割，避免重复处理

#### 使用方法

```bash
# 默认模式：自动检查数据新鲜度，增量更新
python3 lpr_scraper_integrated.py

# 增量更新模式：只更新有变化的年份数据
python3 lpr_scraper_integrated.py --incremental-only

# 强制重新爬取所有数据
python3 lpr_scraper_integrated.py --force
```

#### 工作流程
1. 📂 加载已存在的年份数据文件
2. 🌐 爬取最新的完整LPR数据
3. 🔍 智能比较新旧数据，识别需要更新的年份
4. 💾 直接保存需要更新的年份文件
5. 📦 同时生成完整数据文件（保持兼容性）

#### 输出文件
- **年份数据**: `yearly_data/LPR_Data_YYYY.csv` 和 `LPR_Data_YYYY.json`
- **完整数据**: `LPR_Data.csv`, `LPR_Data.json`, `LPR_Data.txt`（保持兼容性）

### 2. LPR基础爬取工具 (`lpr_scraper.py`) - 简单模式

#### 功能特性
- 🌐 从中国银行官网自动爬取LPR数据
- 📅 自动检测数据是否需要更新
- 💾 支持多种输出格式（CSV、JSON、TXT）
- 🔧 保持向后兼容性

#### 使用方法

```bash
# 正常爬取（检查数据新鲜度）
python3 lpr_scraper.py

# 强制重新爬取
python3 lpr_scraper.py --force
```

#### 输出文件
- `LPR_Data.csv`: CSV格式数据，包含日期、一年期LPR、五年期以上LPR
- `LPR_Data.json`: JSON格式数据，包含元信息和记录数组
- `LPR_Data.txt`: 原始文本格式，保持与源网站一致

#### 注意事项
- 此工具只进行数据爬取，不按年份分割
- 如需按年份分割功能，请使用集成工具 `lpr_scraper_integrated.py`
- 适用于只需要完整数据文件的简单场景

## 🔄 GitHub Actions Workflows

### Workflow 1: `update-lpr-data.yml` - 主数据更新

**触发条件:**
- 定时触发：每天北京时间上午10点（UTC时间凌晨2点）
- 手动触发：可在 Actions 页面手动运行
- 代码变更：当相关文件变更时

**执行流程:**
1. 🕷️ **集成爬取和分割**: 使用 `lpr_scraper_integrated.py` 一次完成数据爬取和按年份分割
2. 🔄 **智能增量更新**: 自动比较新旧数据，只更新有变化的年份
3. 📤 自动提交和推送更新
4. 📦 上传数据文件为artifacts

### Workflow 2: `split-lpr-data.yml` - 数据分割

**触发条件:**
- 手动触发：支持指定年份和强制重新导出
- 主数据更新：当 `LPR_Data.csv` 更新时
- 主workflow完成：当数据更新workflow成功完成时

**手动触发参数:**
- `year`: 指定年份（如2023），不填则导出所有年份
- `force`: 是否强制重新导出（true/false）

**主要功能:**
- 🔄 **增量更新**: 使用集成工具进行智能增量更新
- 🎯 支持强制重新更新所有数据
- 📊 生成详细的更新报告
- 🧹 自动清理旧的artifacts

### Workflow 3: `data-quality-check.yml` - 数据质量检查

**触发条件:**
- 定时触发：每周一北京时间下午2点（UTC时间上午6点）
- 手动触发：可随时运行检查
- 数据变更：当相关文件变更时

**主要功能:**
- 🔍 检查数据文件完整性
- 📈 分析数据统计信息
- 🕒 检查数据新鲜度
- 📝 生成质量报告

## 🚀 手动操作指南

### 手动触发数据更新
1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Update LPR Data" workflow
3. 点击 "Run workflow" 按钮

### 手动分割指定年份数据
1. 进入 Actions 页面
2. 选择 "Split LPR Data by Year" workflow
3. 点击 "Run workflow"
4. 填写参数：
   - **年份**: 输入要分割的年份（如2023），留空则分割所有年份
   - **强制重新导出**: 选择是否强制覆盖已有文件

### 手动运行数据质量检查
1. 进入 Actions 页面
2. 选择 "LPR Data Quality Check" workflow
3. 点击 "Run workflow"

## 📊 数据统计

### 当前数据覆盖情况
- **数据年份**: 2019-2025年
- **记录统计**:
  - 2019年：5条记录
  - 2020年：12条记录
  - 2021年：12条记录
  - 2022年：12条记录
  - 2023年：12条记录
  - 2024年：12条记录
  - 2025年：10条记录
- **总计**: 75条记录

### 输出结果（Artifacts）
每次workflow运行都会生成可下载的artifacts：
- **lpr-data-{run_number}**: 完整的数据文件
- **yearly-lpr-data-{run_number}**: 按年份分割的数据
- **data-quality-report-{run_number}**: 数据质量报告

## 📈 使用场景

### 1. 按年份分析
方便进行特定年份的LPR数据分析，避免处理过大的数据文件。

### 2. 增量备份
只备份新增的年份数据，节省存储空间和传输时间。

### 3. 数据分发
可以只分享特定年份的数据，保护其他年份数据的隐私。

### 4. 性能优化
避免加载过大的完整数据文件，提高应用响应速度。

### 5. API服务
可以基于年份数据构建API服务，提供按年份查询功能。

## 🛠️ 故障排除

### 常见问题

1. **数据爬取失败**
   - 检查目标网站是否可访问
   - 查看workflow日志中的错误信息
   - 可能需要更新爬虫代码适配网站变更

2. **数据分割失败**
   - 确保 `LPR_Data.csv` 文件存在且格式正确
   - 检查 `lpr_data_splitter.py` 代码是否有语法错误
   - 查看权限设置是否正确

3. **提交失败**
   - 检查 GITHUB_TOKEN 权限
   - 确认仓库设置允许 Actions 写入内容
   - 可能需要配置 PAT（Personal Access Token）

### 调试技巧

1. **查看详细日志**
   - 进入 Actions 页面
   - 点击具体的 workflow run
   - 展开各个步骤查看详细输出

2. **本地测试**
   ```bash
   # 本地测试数据爬取
   python lpr_scraper.py --force

   # 本地测试数据分割
   python lpr_data_splitter.py
   ```

3. **检查文件状态**
   ```bash
   # 检查数据文件
   ls -la LPR_Data.* yearly_data/

   # 检查数据完整性
   wc -l LPR_Data.csv yearly_data/*.csv
   ```

## ⚙️ 配置说明

### 权限要求
- `contents: write`: 用于自动提交和推送代码
- `actions: read`: 读取 actions 信息
- `actions: write`: 用于清理 artifacts（仅在 quality check workflow）

### 环境要求
- Python 3.9
- 依赖包：`requests`, `beautifulsoup4`
- Ubuntu 最新版本

### 定时任务
- **数据更新**: 每天 UTC 02:00（北京时间 10:00）
- **质量检查**: 每周一 UTC 06:00（北京时间 14:00）

## 📈 性能优化和对比

### 工具选择对比

| 特性 | 集成工具 (`lpr_scraper_integrated.py`) | 基础工具 (`lpr_scraper.py`) |
|------|-------------------------------------|---------------------------|
| **主要功能** | 爬取 + 分割 + 增量更新 | 仅爬取 |
| **处理步骤** | 1步完成 | 1步完成 |
| **年份数据** | ✅ 自动按年份分割 | ❌ 不分割 |
| **增量更新** | ✅ 智能识别变化年份 | ❌ 无 |
| **处理时间** | 快（一次完成） | 快（仅爬取） |
| **推荐场景** | 日常使用、自动化 | 仅需完整数据、调试 |

### 性能优势

1. **🚀 单步处理**: 一次运行完成爬取和分割，减少50%的处理时间
2. **🎯 精准更新**: 只更新有变化的年份，避免不必要的文件操作
3. **💾 内存优化**: 流式处理，避免同时加载大量数据
4. **🔄 智能比较**: 基于数据内容而非文件时间进行增量判断
5. **⚡ 并行友好**: 各年份独立处理，天然支持并行化

### 自动化优化

1. **增量更新**: 只在数据变化时重新处理
2. **并行处理**: 多个年份可以并行处理
3. **Artifact清理**: 自动删除旧的 artifacts 节省存储
4. **智能跳过**: 基于数据内容避免重复处理

## 🔧 自定义配置

### 修改触发时间
编辑相应 workflow 文件中的 `cron` 表达式：
```yaml
schedule:
  - cron: '0 2 * * *'  # UTC时间每天凌晨2点
```

### 修改保留策略
调整 artifact 保留天数：
```yaml
retention-days: 30  # 保留30天
```

### 添加通知
可以在 workflow 中添加通知步骤，如发送邮件或 Slack 消息。

## 📝 数据格式说明

### CSV格式说明
- **字段顺序**: 日期, 一年期LPR(%), 五年期以上LPR(%)
- **日期格式**: YYYY-MM-DD
- **利率格式**: 数值，不包含百分号
- **排序**: 按日期从新到旧排序

### JSON格式说明
- **year**: 数据年份
- **total_records**: 记录总数
- **date_range**: 数据日期范围（start/end）
- **last_updated**: 最后更新时间（ISO格式）
- **data**: 数据记录数组

## 📞 支持与反馈

如果遇到问题或需要改进建议，请：
1. 查看 Actions 页面的运行日志
2. 检查 Issues 页面是否已有相关问题
3. 创建新的 Issue 描述问题详情

## 🔄 版本更新

- **v1.0**: 基础数据爬取功能
- **v2.0**: 增加数据分割功能
- **v3.0**: 完整的GitHub Actions workflows
- **v3.1**: 数据质量检查和监控

---

*最后更新: 2025-10-31*
*版本: v3.1*