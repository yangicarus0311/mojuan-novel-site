# 墨卷 - 网文小说网站

一个沉浸式阅读体验的网文小说网站，采用 Vue 3 + FastAPI + MySQL 技术栈。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | MySQL 8 |
| 文件存储 | 本地文件系统 |

## 项目结构

```
novel-site/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic 模型
│   │   ├── services/    # 业务逻辑
│   │   ├── core/         # 核心配置
│   │   └── main.py       # 入口文件
│   ├── uploads/          # 上传文件目录
│   ├── requirements.txt
│   └── .env              # 环境变量
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── components/  # 公共组件
│   │   ├── stores/       # Pinia 状态管理
│   │   ├── api/          # API 封装
│   │   └── router/       # 路由配置
│   └── package.json
└── docker-compose.yml    # MySQL 容器配置
```

## 快速启动

### 1. 启动数据库

```bash
cd novel-site
docker-compose up -d
```

### 2. 启动后端

```bash
# 创建虚拟环境
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

后端运行在 http://localhost:8000

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

## API 文档

启动后端后访问：http://localhost:8000/docs

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 用户注册 |
| POST | /api/auth/login | 用户登录 |
| GET | /api/works | 作品列表 |
| GET | /api/works/{id} | 作品详情 |
| GET | /api/works/{id}/chapters | 章节目录 |
| GET | /api/chapters/{id} | 章节内容 |
| GET | /api/bookshelf | 书架列表 |
| POST | /api/bookshelf/{work_id} | 加入书架 |
| DELETE | /api/bookshelf/{work_id} | 移出书架 |
| GET | /api/search | 搜索作品 |

## 功能特性

- [x] 用户注册/登录 (JWT)
- [x] 作品浏览（分类、筛选）
- [x] 作品详情
- [x] 章节阅读
- [x] 书架收藏
- [x] 阅读进度记录
- [x] 作品搜索
- [x] 排行榜

## 开发说明

### 数据库模型

- **User**: 用户
- **Work**: 作品
- **Chapter**: 章节
- **Bookshelf**: 书架
- **ReadProgress**: 阅读进度

### 前端页面

- `/` - 首页
- `/login` - 登录
- `/register` - 注册
- `/works/:id` - 作品详情
- `/works/:workId/chapters/:chapterId` - 阅读页
- `/bookshelf` - 书架
- `/search` - 搜索

## License

MIT
