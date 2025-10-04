# GitHub Secrets Setup Guide

To enable automated cloud scheduling, you need to configure the following secrets in your GitHub repository.

## Steps to Add Secrets:

1. Go to your repository: https://github.com/chaizhuoyuan/stock_monitor
2. Click on "Settings" tab
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click "New repository secret" for each secret below

## Required Secrets:

### 1. STOCK_MONITOR_CONFIG
This should contain your entire configuration JSON:

```json
{
  "tushare": {
    "api_key": "bb30a9f53019f70a1bbf2edb5d67587974a0cc5cde8f11f680672261"
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "chatgptt07@gmail.com",
    "password": "dpzudrpsdjrsvxgb",
    "receivers": ["chaizhuoyuan@gmail.com", "felixochai@gmail.com", "1914861911@qq.com"],
    "use_tls": true
  },
  "stock_list_path": "Targetstocklist.csv",
  "schedule": {
    "run_time": "15:30"
  }
}
```

### 2. STOCK_LIST
This should contain your CSV file content. Copy the entire content from your Targetstocklist.csv file.

## Enabling GitHub Actions:

1. Go to the "Actions" tab in your repository
2. If Actions are not enabled, click "Enable Actions"
3. The workflow will run automatically:
   - Every weekday at 15:30 Beijing time (7:30 UTC)
   - You can also trigger it manually from the Actions tab

## Manual Trigger:

1. Go to Actions tab
2. Select "Daily Stock Monitor" workflow
3. Click "Run workflow" button
4. Select branch "main"
5. Click "Run workflow"

## Monitoring:

- Check the Actions tab to see workflow runs
- Each run's logs are saved as artifacts for 30 days
- You'll receive email alerts when stocks breach MAs