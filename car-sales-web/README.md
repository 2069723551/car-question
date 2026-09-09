# 汽车销量预测系统 - 前端（Vue3 + Vite）

基于 Vue3 + Vite + ECharts 的销量预测可视化网页，前后端分离，调用 FastAPI 后端接口。

## 目录结构

```
car-sales-web/
├── package.json            # 依赖与脚本（npm run dev）
├── vite.config.js          # Vite 配置（端口 5174，/api 代理到后端）
├── index.html
├── public/
│   └── favicon.svg
└── src/
    ├── main.js             # 应用入口（Pinia + Router）
    ├── App.vue             # 导航栏 + 页面容器
    ├── api/
    │   └── index.js        # axios 实例 + 后端接口封装（含 db-stats / logs）
    ├── router/
    │   └── index.js        # 路由（首页/数据/模型/数据管理/关于）
    └── views/
        ├── HomeView.vue    # 项目概览（关键指标）
        ├── DataView.vue    # 数据可视化（趋势图/多序列/季节分解）
        ├── ModelView.vue   # 模型预测（R²对比/回归预测/未来预测）
        ├── DbView.vue      # 数据管理（数据库状态/查询日志/数据表预览）
        └── AboutView.vue   # 关于项目
```

## 环境要求

- Node.js 18+（本项目开发环境为 Node 20）
- 依赖：`vue`、`vue-router`、`pinia`、`axios`、`echarts`、`vite`

## 启动方式（PyCharm）

1. 用 PyCharm 打开本目录 `car-sales-web`
2. 终端执行 `npm install`（首次需安装依赖）
3. 终端执行 `npm run dev`
4. 浏览器访问 `http://localhost:5174`

> 注意：前端端口为 **5174**（5173 可能被其他 Vue 项目占用）。
> 如 5174 被占用，Vite 会自动改用 5175，以终端输出为准。

## 页面说明

| 路由 | 页面 | 说明 |
|---|---|---|
| `/home` | 项目概览 | 项目简介、关键指标、数据集概览、模型对比表 |
| `/data` | 数据可视化 | 主序列趋势、新车/二手车对比、季节分解 |
| `/model` | 模型预测 | 四模型 R² 对比、回归预测、未来 12 个月预测、特征重要性 |
| `/db` | 数据管理 | SQLite 数据库状态、接口查询日志、数据表预览 |
| `/about` | 关于项目 | 项目说明、技术栈、数据来源、运行方式 |

## 联调说明

- 后端需先启动：在 `car-sales-backend` 运行 `python main.py`（http://127.0.0.1:8000）
- 前端 `src/api/index.js` 中 `baseURL` 指向 `http://127.0.0.1:8000`
- `vite.config.js` 已配置 `/api` 与 `/figures` 代理到后端，也可直接使用相对路径
