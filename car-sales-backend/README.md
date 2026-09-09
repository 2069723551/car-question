# 汽车销量预测系统 - 后端（FastAPI + SQLite）

提供销量数据、模型指标、未来预测等接口，供前端 Vue 项目调用。数据存储在 SQLite 数据库，启动时自动建表并导入 CSV 数据。

## 目录结构

```
car-sales-backend/
├── main.py                 # FastAPI 入口（端口 8000，含 CORS，启动建表+导数据）
├── requirements.txt        # 依赖清单
├── car_sales.db            # SQLite 数据库文件（首次启动自动生成）
├── core/
│   ├── config.py           # 数据/输出路径配置 + DATABASE_URL
│   └── database.py         # SQLAlchemy 引擎与会话（get_db）
├── models/
│   └── sales.py            # 数据表定义：sales_records / prediction_records / query_logs
├── crud/
│   └── sales.py            # 三张表的增删查改操作
├── schemas/
│   └── sales.py            # Pydantic 响应模型
├── routers/
│   └── sales.py            # API 路由（查询走数据库 + 自动记录查询日志）
├── services/
│   ├── data_service.py     # 加载数据集（概览/辅助序列）
│   ├── forecast_service.py # 读取模型指标与预测结果
│   └── db_service.py       # 数据库初始化与 CSV 数据导入
├── data/                   # 两个公开数据集 CSV
└── output/
    ├── predictions/        # 模型指标与预测结果（metrics.json、未来预测 CSV）
    └── figures/            # 6 张可视化图表 PNG
```

## 数据库说明（三张表）

| 表名 | 内容 | 条数 |
|---|---|---|
| `sales_records` | 主数据集月度销量（从 CSV 导入） | 108 |
| `prediction_records` | 未来 12 个月销量预测（从 CSV 导入） | 12 |
| `query_logs` | 接口查询日志（每次 API 调用自动写入） | 动态增长 |

- 数据库文件：`car_sales.db`（首次启动自动生成）
- 启动时自动建表并导入数据（幂等：已有数据则跳过）
- `/api/series`、`/api/forecast` 从数据库读取

## 环境要求

- Python 3.9+
- 依赖：`fastapi`、`uvicorn`、`pandas`、`sqlalchemy`

## 启动方式（PyCharm）

1. 用 PyCharm 打开本目录 `car-sales-backend`
2. 配置 Python 解释器（File → Settings → Project → Python Interpreter，选择你的 Python 3.12）
3. 安装依赖：终端执行 `pip install -r requirements.txt`
4. 运行 `main.py`（右键 Run，或终端执行 `python main.py`）
5. 看到日志 `Uvicorn running on http://0.0.0.0:8000` 即启动成功

## 接口列表

| 接口 | 说明 |
|---|---|
| `GET /` | 服务信息 |
| `GET /api/overview` | 数据集概览（记录数、时间范围、统计量） |
| `GET /api/series` | 主数据集月度销量序列（**从数据库读取**） |
| `GET /api/multi-series` | 辅助数据集新车/二手车登记序列 |
| `GET /api/metrics` | 四类模型评估指标 |
| `GET /api/forecast` | 未来 12 个月销量预测（**从数据库读取**） |
| `GET /api/regression` | 回归模型测试集真实值 vs 预测值 |
| `GET /api/figures` | 可视化图表文件列表 |
| `GET /api/db-stats` | 数据库状态（三张表记录数） |
| `GET /api/logs` | 最近接口查询日志（默认 20 条） |
| `GET /figures/{name}` | 图表图片 |

接口文档：启动后访问 `http://127.0.0.1:8000/docs`

## 说明

- 数据与预测结果为离线训练产物，启动即用，无需重新训练
- 前端默认请求 `http://127.0.0.1:8000`，如修改端口需同步修改前端 `src/api/index.js`
