import datetime
import json
import numpy as np
from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# --- 1. 数据库基础设施 (SQLAlchemy) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./sensor_data.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SensorRecord(Base):
    __tablename__ = "sensor_logs"
    id = Column(Integer, primary_key=True, index=True)
    temp = Column(Float, nullable=False)
    hum = Column(Float, nullable=False)
    coll_time = Column(String, nullable=False)  # 采集时间
    save_time = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)) # 入库时间

Base.metadata.create_all(bind=engine)

# --- 2. FastAPI 实例与模型 ---
app = FastAPI(title="传感器分析中心")

class DataPayload(BaseModel):
    time: str
    temp: float
    hum: float

# --- 3. 核心业务端点 ---

@app.post("/upload")
async def upload_data(payload: DataPayload):
    """接收并持久化传感器数据"""
    db = SessionLocal()
    try:
        new_record = SensorRecord(
            temp=payload.temp,
            hum=payload.hum,
            coll_time=payload.time
        )
        db.add(new_record)
        db.commit()
        return {"status": "success", "received_at": payload.time}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
    finally:
        db.close()

@app.get("/view", response_class=HTMLResponse)
async def view_dashboard():
    """图形化监控看板"""
    db = SessionLocal()
    try:
        records = db.query(SensorRecord).order_by(SensorRecord.id.desc()).limit(100).all()
        labels = [r.coll_time for r in reversed(records)]
        temp_list = [r.temp for r in reversed(records)]
        hum_list = [r.hum for r in reversed(records)]

        html_template = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <title>传感器实时监测</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    body {{ font-family: "PingFang SC", "Microsoft YaHei", sans-serif; margin: 30px; background: #f8f9fa; }}
                    .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    h2 {{ color: #2d3436; text-align: center; }}
                    .nav {{ margin-top: 20px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>环境数据实时监控 (最近100个样本)</h2>
                    <canvas id="sensorChart"></canvas>
                </div>
                <div class="nav">
                    <button onclick="window.location.href='/analyze'">查看网络性能分析报告</button>
                </div>
                <script>
                    const ctx = document.getElementById('sensorChart').getContext('2d');
                    new Chart(ctx, {{
                        type: 'line',
                        data: {{
                            labels: {json.dumps(labels)},
                            datasets: [
                                {{ label: '温度 (°C)', data: {json.dumps(temp_list)}, borderColor: '#ff4d4f', tension: 0.3, fill: false }},
                                {{ label: '湿度 (%)', data: {json.dumps(hum_list)}, borderColor: '#1890ff', tension: 0.3, fill: false }}
                            ]
                        }},
                        options: {{ responsive: true, plugins: {{ legend: {{ position: 'top' }} }} }}
                    }});
                </script>
            </body>
        </html>
        """
        return HTMLResponse(content=html_template)
    finally:
        db.close()

@app.get("/analyze", response_class=HTMLResponse)
async def analyze_performance(limit: int = Query(100, gt=1)):
    """网络性能诊断端点 (中文版)"""
    db = SessionLocal()
    try:
        records = db.query(SensorRecord).order_by(SensorRecord.id.desc()).limit(limit).all()
        if not records:
            return "<html><body style='background:#121212;color:white;'><h3>暂无可用分析数据。</h3></body></html>"

        latencies = []
        out_of_order = 0
        last_c_time = None

        for r in reversed(records):
            try:
                # 解析采集时间并统一时区
                c_time = datetime.datetime.strptime(r.coll_time, "%Y-%m-%d %H:%M:%S")
                c_time = c_time.replace(tzinfo=datetime.timezone.utc)
                # 获取服务器存储时间
                s_time = r.save_time if r.save_time.tzinfo else r.save_time.replace(tzinfo=datetime.timezone.utc)
                
                # 计算传输延迟
                delay = (s_time - c_time).total_seconds()
                latencies.append(delay)

                # 检查时序逻辑一致性
                if last_c_time and c_time < last_c_time:
                    out_of_order += 1
                last_c_time = c_time
            except ValueError:
                continue

        # 统计学分析
        avg_lat = np.mean(latencies) if latencies else 0
        jitter = np.std(latencies) if latencies else 0
        consistency = ((len(records) - out_of_order) / len(records)) * 100

        analysis_html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <title>网络性能深度分析</title>
                <style>
                    body {{ font-family: "Consolas", "Monaco", monospace; background: #0e1111; color: #00ff41; padding: 40px; line-height: 1.6; }}
                    .report-container {{ border: 2px solid #00ff41; padding: 30px; border-radius: 8px; max-width: 800px; margin: auto; }}
                    .metric {{ margin: 15px 0; font-size: 1.2em; border-bottom: 1px dotted #333; padding-bottom: 10px; }}
                    .value {{ color: #ffffff; font-weight: bold; }}
                    .critical {{ color: #ff3e3e; text-decoration: underline; }}
                    .header {{ text-align: center; border-bottom: 2px solid #00ff41; margin-bottom: 30px; }}
                    a {{ color: #00ff41; text-decoration: none; border: 1px solid #00ff41; padding: 5px 10px; }}
                    a:hover {{ background: #00ff41; color: #000; }}
                </style>
            </head>
            <body>
                <div class="report-container">
                    <div class="header">
                        <h1>网络传输性能诊断报告</h1>
                    </div>
                    <div class="metric">平均传输延迟: <span class="value">{avg_lat:.4f} 秒</span></div>
                    <div class="metric">网络抖动 (标准差): <span class="value">{jitter:.4f} 秒</span></div>
                    <div class="metric">时序一致性评分: <span class="value {'critical' if consistency < 100 else ''}">{consistency:.2f}%</span></div>
                    <div class="metric">分析样本规模: <span class="value">{len(records)} 组</span></div>
                    <div class="metric">系统可用性状态: <span class="value">运行正常 (Active)</span></div>
                    
                    <div style="margin-top: 40px; text-align: center;">
                        <a href="/view">返回数据看板</a>
                    </div>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=analysis_html)
    finally:
        db.close()
