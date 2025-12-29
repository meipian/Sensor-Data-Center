<img width="2951" height="1662" alt="image" src="https://github.com/user-attachments/assets/4b47d3ab-c08f-433c-8818-c9c08afd760a" />

# Sensor Data Center

### 项目介绍

本项目是一个基于 **FastAPI** 和 **SQLAlchemy** 的传感器数据采集与可视化中心。其核心功能是接收远程传感器通过 HTTP POST 协议上传的 JSON 数据，并将其持久化至 SQLite 数据库。同时，系统提供了一个基于 Chart.js 的 Web 端点，用于时序数据的图形化实时监控。

---

### 快速导航

1. [项目架构说明](https://www.google.com/search?q=%23%E9%A1%B9%E7%9B%AE%E6%9E%B6%E6%9E%84%E8%AF%B4%E6%98%8E)
2. [快速上手指南 (Windows)](https://www.google.com/search?q=%23%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B%E6%8C%87%E5%8D%97-windows)

---

## 项目架构说明

本项目遵循经典的 **三层解耦架构**，确保了数据流向的确定性与可维护性：

* **接入层 (Access Layer)**：利用 FastAPI 异步框架处理并发请求。通过 Pydantic 模块进行强类型校验，拒绝格式异常的非理性数据。
* **持久层 (Persistence Layer)**：采用 SQLAlchemy ORM 框架，底层使用 SQLite 数据库。通过 `SessionLocal` 管理数据库事务，确保数据一致性。
* **表现层 (Presentation Layer)**：后端生成动态 HTML 响应，前端通过 CDN 引入 Chart.js。数据通过 JSON 序列化注入前端上下文，实现无缝的时序图表渲染。

---

## 快速上手指南 (Windows)

### 1. 环境准备

确保系统已安装 **Python 3.12+**：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install fastapi sqlalchemy uvicorn pydantic -i https://pypi.tuna.tsinghua.edu.cn/simple
uvicorn app:app --reload --host 127.0.0.1 --port 8000
python sender.py
```

### 5. 访问端点

* **数据视图**: 请访问 `http://127.0.0.1:8000/view`
* **网络性能分析**: 请访问 `http://127.0.0.1:8000/analeze` 

---

