import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 配置信息 - 使用GitHub Secrets
EMAIL_CONFIG = {
    'smtp_server': 'smtp.vip.163.com',
    'smtp_port': 465,
    'sender_email': 'ybuwuxin@vip.163.com',
    'sender_password': os.environ.get('EMAIL_PASSWORD'),
    'receiver_email': 'ybuwuxin@vip.163.com'
}

AMAP_CONFIG = {
    'api_key': os.environ.get('AMAP_API_KEY'),
    'city': '320115'
}

def get_weather_forecast():
    """使用高德地图API获取天气预报信息"""
    if not AMAP_CONFIG['api_key']:
        print("❌ 高德地图API密钥未配置")
        return None
        
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    params = {
        'key': AMAP_CONFIG['api_key'],
        'city': AMAP_CONFIG['city'],
        'extensions': 'all',
        'output': 'JSON'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"✅ 高德API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == '1' and data['infocode'] == '10000':
                if 'forecasts' in data and len(data['forecasts']) > 0:
                    forecast_data = data['forecasts'][0]
                    today_forecast = forecast_data['casts'][0]
                    
                    return {
                        'city': forecast_data['city'],
                        'date': today_forecast['date'],
                        'week': today_forecast['week'],
                        'day_weather': today_forecast['dayweather'],
                        'night_weather': today_forecast['nightweather'],
                        'day_temp': today_forecast['daytemp'],
                        'night_temp': today_forecast['nighttemp'],
                        'day_wind': today_forecast['daywind'],
                        'night_wind': today_forecast['nightwind'],
                        'day_power': today_forecast['daypower'],
                        'night_power': today_forecast['nightpower'],
                        'report_time': forecast_data['reporttime']
                    }
            else:
                print(f"❌ 高德API错误: {data.get('info', '未知错误')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 获取天气预报失败: {e}")
    
    return None

def get_current_weather():
    """获取实时天气作为备用"""
    if not AMAP_CONFIG['api_key']:
        return None
        
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    params = {
        'key': AMAP_CONFIG['api_key'],
        'city': AMAP_CONFIG['city'],
        'extensions': 'base',
        'output': 'JSON'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1' and data['infocode'] == '10000':
                if 'lives' in data and len(data['lives']) > 0:
                    weather_info = data['lives'][0]
                    return {
                        'city': weather_info['city'],
                        'weather': weather_info['weather'],
                        'temperature': weather_info['temperature'],
                        'wind_direction': weather_info['winddirection'],
                        'wind_power': weather_info['windpower'],
                        'humidity': weather_info['humidity'],
                        'report_time': weather_info['reporttime'],
                        'is_current': True
                    }
    except Exception as e:
        print(f"❌ 获取实时天气失败: {e}")
    
    return None

def format_weather_info(weather_data):
    """格式化天气信息"""
    if not weather_data:
        return "暂无天气数据"
        
    if weather_data.get('is_current'):
        return f"""
        <p><b>当前天气：</b>{weather_data['weather']}</p>
        <p><b>当前温度：</b>{weather_data['temperature']}°C</p>
        <p><b>湿度：</b>{weather_data['humidity']}%</p>
        <p><b>风向风力：</b>{weather_data['wind_direction']} {weather_data['wind_power']}级</p>
        """
    else:
        weather_phenomenon = weather_data['day_weather']
        if weather_data['day_weather'] != weather_data['night_weather']:
            weather_phenomenon = f"{weather_data['day_weather']}转{weather_data['night_weather']}"
        
        temp_range = f"{weather_data['night_temp']}~{weather_data['day_temp']}°C"
        
        return f"""
        <p><b>日期：</b>{weather_data['date']} 星期{weather_data['week']}</p>
        <p><b>天气：</b>{weather_phenomenon}</p>
        <p><b>温度范围：</b>{temp_range}</p>
        <p><b>白天：</b>{weather_data['day_weather']}，{weather_data['day_temp']}°C，{weather_data['day_wind']}风{weather_data['day_power']}级</p>
        <p><b>夜间：</b>{weather_data['night_weather']}，{weather_data['night_temp']}°C，{weather_data['night_wind']}风{weather_data['night_power']}级</p>
        """

def send_weather_email():
    """发送天气邮件"""
    if not EMAIL_CONFIG['sender_password']:
        print("❌ 邮箱密码未配置")
        return False
        
    # 获取天气数据
    weather = get_weather_forecast()
    weather_type = "预报"
    
    if not weather:
        weather = get_current_weather()
        weather_type = "实时"
    
    if not weather:
        return send_test_email()

    # 构建邮件内容
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    subject = f"今日天气{weather_type}报告 - {current_time.split()[0]}"
    
    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            .header {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            .weather-info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .footer {{ color: #7f8c8d; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🌅 早安！今日天气{weather_type}报告</h2>
            <p>报告时间：{current_time}</p>
            <p>数据来源：高德地图天气API</p>
        </div>
        
        <div class="weather-info">
            <h3>📍 {weather['city']}</h3>
            {format_weather_info(weather)}
        </div>
        
        <div class="footer">
            <p>更新时间：{weather['report_time']}</p>
            <p>💡 祝您有美好的一天！</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG['sender_email']
    msg['To'] = EMAIL_CONFIG['receiver_email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        print(f"✅ {current_time} - 天气{weather_type}邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def send_test_email():
    """发送测试邮件"""
    if not EMAIL_CONFIG['sender_password']:
        print("❌ 邮箱密码未配置")
        return False
        
    subject = f"天气服务测试 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body = f"""
    <h2>天气邮件服务测试</h2>
    <p>发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <hr>
    <p>✅ 邮件发送功能正常</p>
    <p>⚠️ 天气API配置检查中...</p>
    """

    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG['sender_email']
    msg['To'] = EMAIL_CONFIG['receiver_email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        print("✅ 测试邮件发送成功！")
        return True
    except Exception as e:
        print(f"❌ 测试邮件发送失败: {e}")
        return False

if __name__ == "__main__":
    send_weather_email()
