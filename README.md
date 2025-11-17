# 天气邮件服务

自动发送每日天气预报邮件的GitHub Actions服务。

## 功能特点

- 🌦️ 获取江宁区天气预报（温度范围、天气变化）
- 📧 自动发送HTML格式的天气邮件
- ⏰ 每天定时运行（可自定义时间）
- 🔒 使用GitHub Secrets保护敏感信息
- 📱 响应式邮件设计

## 配置说明

### 必需的环境变量

在GitHub仓库的Settings → Secrets中配置：

- `EMAIL_PASSWORD`: 163邮箱SMTP授权码
- `AMAP_API_KEY`: 高德地图API密钥

### 定时任务配置

修改 `.github/workflows/weather-email.yml` 中的cron表达式：
