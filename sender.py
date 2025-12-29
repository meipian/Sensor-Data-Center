import time
import json
import random
import logging
import requests
from datetime import datetime, timedelta
from itertools import count
from typing import Final, Dict, Any

# --- 配置常量 ---
TARGET_URL: Final[str] = "http://127.0.0.1:8000/upload"  # 预留URL接口
SEND_INTERVAL: Final[int] = 1  # 发送间隔（秒）

# 模拟参数配置：均值(mu) 与 标准差(sigma)
TEMP_MU: Final[float] = 25.5
TEMP_SIGMA: Final[float] = 0.5

HUM_MU: Final[float] = 45.0
HUM_SIGMA: Final[float] = 1.0

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SensorSender:
    """
    传感器数据模拟发送器
    """
    def __init__(self, url: str):
        self.url = url
        self._time_stepper = count(start=0, step=1)
        # 基准时间，用于构造递增时间戳
        self.base_time = datetime.now()

    def _generate_payload(self) -> Dict[str, Any]:
        """
        构造符合物理事实的JSON报文
        """
        current_step = next(self._time_stepper)
        
        # 构造趋于稳定的随机数
        temp = round(random.gauss(TEMP_MU, TEMP_SIGMA), 2)
        hum = round(random.gauss(HUM_MU, HUM_SIGMA), 2)
        
        # 构造递增时间字段 (ISO 8601 格式)
        timestamp = (self.base_time + timedelta(seconds=current_step)).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "time": timestamp,
            "temp": temp,
            "hum": hum,
            "step_id": current_step
        }

    def run(self):
        """
        主循环执行逻辑
        """
        logging.info(f"Starting sender service. Target: {self.url}")
        
        try:
            while True:
                payload = self._generate_payload()
                
                try:
                    # 预留发送逻辑，设置超时以防阻塞
                    response = requests.post(
                        self.url, 
                        json=payload, 
                        timeout=5
                    )
                    logging.info(f"Sent: {payload} | Status: {response.status_code}")
                
                except requests.exceptions.RequestException as e:
                    logging.error(f"Network Error: {payload['step_id']} failed to send. Reason: {e}")
                
                time.sleep(SEND_INTERVAL)
                
        except KeyboardInterrupt:
            logging.info("Process terminated by user.")

if __name__ == "__main__":
    sender = SensorSender(TARGET_URL)
    sender.run()
