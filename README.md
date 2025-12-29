<img width="2951" height="1662" alt="image" src="https://github.com/user-attachments/assets/4b47d3ab-c08f-433c-8818-c9c08afd760a" />

# Sensor Data Center

### 项目介绍

本项目是一个基于 **FastAPI** 和 **SQLAlchemy** 的传感器数据采集与可视化中心。其核心功能是接收远程传感器通过 HTTP POST 协议上传的 JSON 数据，并将其持久化至 SQLite 数据库。同时，系统提供了一个基于 Chart.js 的 Web 端点，用于时序数据的图形化实时监控。

---

### 项目特点

1. 提供独立的测试程序`sender.py`
2. 支持**网络性能分析**

### 快速导航

* [1. 项目架构说明](#项目架构说明)
* [2. 快速上手 (Windows)](#快速上手-windows)

---

## 项目架构说明

* **接入层 (Access Layer)**：利用 FastAPI 异步框架处理并发请求。通过 Pydantic 模块进行强类型校验，拒绝格式异常的非理性数据。
* **持久层 (Persistence Layer)**：采用 SQLAlchemy ORM 框架，底层使用 SQLite 数据库。通过 `SessionLocal` 管理数据库事务，确保数据一致性。
* **表现层 (Presentation Layer)**：后端生成动态 HTML 响应，前端通过 CDN 引入 Chart.js。数据通过 JSON 序列化注入前端上下文，实现无缝的时序图表渲染。

---

## 快速上手 (Windows)

### 1. 环境准备

确保您的系统已安装 **Python 3.12+**：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

以 1s 为间隔发送模拟采集数据：

```powershell
python sender.py
```

### 2. 访问端点

* **数据视图**: 请访问 `http://127.0.0.1:8000/view`
* **网络性能分析**: 请访问 `http://127.0.0.1:8000/analyze` 

---

