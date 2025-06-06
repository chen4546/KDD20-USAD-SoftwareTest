import requests
import time
from datetime import datetime


def export_metrics(interval_sec=5, duration_hours=24):
    """持续导出指标数据"""
    end_time = time.time() + duration_hours * 3600


    while time.time() < end_time:
        # 获取当前指标
        response = requests.get("http://127.0.0.1:9100/metrics")
        metrics_data = []
        if response.status_code == 200:
            # 添加时间戳
            timestamp = datetime.now().isoformat()
            metrics_data.append(f"# TIMESTAMP: {timestamp}\n")
            metrics_data.append(response.text)
            print(f"Exported data at {timestamp}")
        # 保存到文件
        with open(f"prometheus_metrics_{datetime.now().strftime('%Y%m%d%H')}.txt", "a") as f:
            f.writelines(metrics_data)
        # 等待下次采集
        time.sleep(interval_sec)




# 每0.05分钟采集一次，持续14小时
export_metrics(interval_sec=1, duration_hours=2)