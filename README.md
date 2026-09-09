# 汽车销量预测系统（完整版）

基于公开汽车销量数据，构建「数据采集与预处理 → 特征工程 → 回归/时间序列预测模型 → 预测结果可视化」的完整机器学习项目，并提供 **FastAPI + Vue3 前后端分离的网页版**（含 SQLite 数据库与智能问答）。

## 一、项目结构

```
汽车销量预测系统/
├── README.md                  # 本说明
├── requirements.txt           # 训练依赖
├── src/                       # 训练源码
│   ├── data_loader.py         # 数据加载与清洗
│   ├── feature_engineer.py    # 特征工程
│   ├── models_regression.py   # 回归模型（线性回归/随机森林）
│   ├── models_timeseries.py   # 时间序列模型（Holt-Winters 等）
│   ├── visualize.py           # 可视化
│   └── main.py                # 训练主流程入口
├── data/                      # 数据集（两个公开 CSV）
├── output/                    # 训练产物（图表 + 预测结果）
├── docs/                      # 6 份课程文档（Word）
├── car-sales-backend/         # 网页版后端（FastAPI + SQLite + 智能预测 + 智能问答）
└── car-sales-web/             # 网页版前端（Vue3 + Vite + ECharts + 智能预测页 + 智能问答页）
```

## 二、数据说明

| 数据集 | 来源 | 时间范围 | 记录数 | 说明 |
|---|---|---|---|---|
| china_car_sales.csv | 中国乘用车月度销量（乘联会 CPCA 登记记录整理，GitHub 公开仓库） | 2018-01~2024-04 | 38806 | 车型-月度销量，含厂商/价格/新能源标记/车身类型/品牌国别 |
| china_monthly.csv | 由 china_car_sales.csv 按月聚合 | 2018-01~2024-04 | 76 | 月度总销量（主预测序列） |

数据均可公开获取、可直接下载（GitHub 公开仓库 CSV 文件），无需登录、不会触发反爬拦截。

## 三、模型训练

```bash
pip install -r requirements.txt
python src/main.py
```

回归模型（线性回归/随机森林，特征含滞后/滚动统计/差分）+ 时间序列模型（季节分解/Holt-Winters），评估指标 MAE / RMSE / R² 输出至 `output/predictions/metrics.json`。

## 四、网页版运行

前后端分离：后端 FastAPI（端口 8000，数据存 SQLite），前端 Vue3（端口 5174）。

### 1. 启动后端（PyCharm 打开 car-sales-backend）

```bash
pip install -r requirements.txt
python main.py
```

启动时自动建表（sales_records / prediction_records / query_logs）并从 CSV 导入数据，接口文档 http://127.0.0.1:8000/docs

### 2. 启动前端（PyCharm 打开 car-sales-web）

```bash
npm install
npm run dev
```

浏览器访问 http://localhost:5174 ，页面含：项目概览（顶部汽车资讯 + 功能板块一键跳转）/ 数据可视化 / 模型预测 / 智能预测（参数预测销量与营销推荐）/ 智能问答（汽车知识库 + 项目数据问答）/ 数据管理（数据库状态与查询日志）/ 关于项目。

## 五、说明

- 网页版后端数据为离线训练产物，启动即用
- 本完整版已清理全部冗余（node_modules、.venv、缓存、日志等），前端需 `npm install`、后端无需额外步骤即可运行

## 六、公开部署（一个网址访问全部功能）

本项目已支持 Docker 单体部署：FastAPI 同域托管 Vue 构建产物，`/api`、`/figures` 和 Vue 子路由都能通过同一个公开网址访问。

### 使用 Render 部署

1. 将本项目根目录上传到 GitHub，并确保仓库为 Public。
2. 在 Render 新建 **Blueprint**，选择该 GitHub 仓库；Render 会自动读取根目录 `render.yaml`。
3. 等待 Docker 构建完成后，打开 Render 分配的 `https://...onrender.com` 地址。
4. 健康检查地址为 `/api/health`，接口文档为 `/docs`。

也可以在本地验证生产镜像：

```bash
docker build -t car-sales-forecast .
docker run --rm -p 8000:8000 car-sales-forecast
```

然后访问 `http://localhost:8000`。GitHub Pages 只能托管静态前端，无法直接运行本项目的 FastAPI、SQLite、预测和问答接口，因此不建议只用 GitHub Pages 发布。