# 股票均线监控系统

这是一个用于监控中国股票是否跌破均线的自动化系统。系统每天定时运行，检查目标股票是否跌破5日、10日、20日均线，并在发现异常时发送邮件告警。

## 功能特点

- 支持从CSV文件读取目标股票列表
- 使用Tushare API获取股票数据
- 计算5日、10日、20日移动平均线
- 检测股价是否跌破均线
- 自动发送邮件告警
- 支持定时任务自动运行
- 完整的错误处理和日志记录

## 安装步骤

1. 克隆或下载项目到本地
```bash
cd /Users/zhuoyuanchai/stopwinning/stock_monitor
```

2. 创建虚拟环境（推荐）
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置文件设置
- 复制 `config/config_template.json` 到 `config/secrets.json`
- 编辑 `config/secrets.json`，填入您的API密钥和邮件配置

## 配置说明

配置文件 `config/secrets.json` 包含以下设置：

```json
{
  "tushare": {
    "api_key": "您的Tushare API密钥"
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "发件人邮箱",
    "password": "应用专用密码",
    "receivers": ["收件人1", "收件人2"],
    "use_tls": true
  },
  "stock_list_path": "股票列表CSV文件路径",
  "schedule": {
    "run_time": "15:30"  // 每天运行时间
  }
}
```

## 股票列表格式

CSV文件应包含股票代码列，支持以下列名：
- `code`
- `stock_code`
- `股票代码`
- `代码`

示例：
```csv
code
600519
000858
002594
```

## 使用方法

### 运行一次分析
```bash
python src/stock_monitor.py --run-once
```

### 测试邮件发送
```bash
python src/stock_monitor.py --test-email
```

### 启动定时任务
```bash
python src/stock_monitor.py --schedule
```

### 使用自定义配置文件
```bash
python src/stock_monitor.py --config /path/to/config.json --run-once
```

## 日志文件

日志文件保存在 `logs/` 目录下，文件名格式为 `stock_monitor_YYYYMMDD.log`

## 注意事项

1. Tushare API有调用频率限制，请确保不要频繁调用
2. Gmail邮箱需要使用应用专用密码，而非账户密码
3. 建议在股市收盘后（15:30之后）运行分析
4. 首次运行建议使用 `--test-email` 测试邮件配置

## 故障排除

1. **邮件发送失败**
   - 检查邮箱是否开启了SMTP服务
   - 确认使用的是应用专用密码
   - 检查网络连接

2. **API调用失败**
   - 确认Tushare API密钥正确
   - 检查是否达到API调用限制
   - 确认网络可以访问Tushare

3. **股票代码无数据**
   - 检查股票代码格式是否正确
   - 确认股票代码在交易所存在

## GitHub Actions部署（可选）

如需在GitHub Actions中运行，可创建以下workflow文件：

`.github/workflows/stock_monitor.yml`:
```yaml
name: Stock Monitor

on:
  schedule:
    - cron: '30 7 * * *'  # UTC时间，相当于北京时间15:30
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run stock monitor
      env:
        CONFIG: ${{ secrets.STOCK_MONITOR_CONFIG }}
      run: |
        echo "$CONFIG" > config/secrets.json
        python src/stock_monitor.py --run-once
```

需要在GitHub仓库的Secrets中设置 `STOCK_MONITOR_CONFIG` 变量，值为完整的配置JSON。