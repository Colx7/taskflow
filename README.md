# TaskFlow - AI 智能任务管理系统

基于 FastAPI + Vue 3 全栈开发的 AI 智能任务管理系统，集成通义千问大模型实现任务自动分类、智能优先级推荐和周报自动生成。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.13, FastAPI, SQLAlchemy 2.0 async, SQLite/MySQL, Alembic |
| 前端 | Vue 3, Vite, Element Plus, Pinia, Vue Router, Axios, ECharts |
| 部署 | Docker, Docker Compose, Nginx |

## 功能特性

- **任务管理**: 完整的 CRUD、筛选、排序、批量操作
- **AI 智能分类**: 自动识别任务分类（工作/学习/生活/健身/其他）和优先级（紧急/高/中/低）
- **AI 周报生成**: 一键生成结构化周报，支持 Markdown 渲染和复制
- **仪表盘统计**: 实时数据概览、趋势图、分类分布饼图
- **JWT 认证**: 安全的 token 登录机制

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 20+
- (可选) Docker & Docker Compose

### 后端启动

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 配置环境变量（可选）
copy .env.example .env

# 初始化种子数据
python seed.py

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

后端运行在 `http://127.0.0.1:8001`，API 文档 `http://127.0.0.1:8001/docs`

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`

### Docker 部署

```bash
# 使用 SQLite（开发环境）
docker compose up -d

# 使用 MySQL（生产环境）
# 编辑 backend/.env 设置 DB_DRIVER=mysql
docker compose up -d
```

## 项目结构

```
TaskFlow/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置
│   │   ├── deps.py          # JWT 认证
│   │   ├── models/          # ORM 模型
│   │   ├── schemas/         # Pydantic DTOs
│   │   ├── routers/         # API 路由
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   ├── seed.py              # 种子数据
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # API 请求
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── views/           # 页面组件
│   │   └── router/          # 路由配置
│   ├── vite.config.ts       # Vite 配置
│   └── Dockerfile.frontend
├── docker-compose.yml
└── nginx/
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/tasks | 获取任务列表 |
| POST | /api/tasks | 创建任务 |
| PUT | /api/tasks/{id} | 更新任务 |
| DELETE | /api/tasks/{id} | 删除任务 |
| POST | /api/ai/classify | AI 智能分类 |
| POST | /api/ai/weekly-report | AI 周报生成 |
| GET | /api/stats/dashboard | 仪表盘统计 |
| GET | /api/stats/trend | 趋势统计 |
| GET | /api/stats/category-distribution | 分类分布 |


## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DB_DRIVER | sqlite | 数据库驱动 (sqlite/mysql) |
| JWT_SECRET_KEY | change-this-to-a-random-secret-key-in-production | JWT 密钥 |
| DASHSCOPE_API_KEY | | 通义千问 API Key |
| AI_MODEL | qwen-plus | AI 模型 |

## 许可证

MIT
