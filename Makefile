.PHONY: install-backend install-frontend db-init dev migrate lint clean

# 安装后端依赖
install-backend:
	cd backend && source venv/bin/activate && pip install -r requirements.txt

# 安装前端依赖
install-frontend:
	cd frontend && npm ci

# 初始化数据库并填充种子数据
db-init:
	cd backend && source venv/bin/activate && python -c "from app.core.database import init_db; init_db()" && python seed.py

# 启动开发服务器（后端 + 前端并行）
dev:
	@echo "Starting backend (uvicorn) and frontend (vite)..."
	@cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@cd frontend && npx vite --host 0.0.0.0 --port 5173

# 运行数据库迁移
migrate:
	cd backend && source venv/bin/activate && alembic upgrade head

# 代码检查（前端 ESLint + 后端 Black）
lint:
	cd frontend && npx eslint src/ --ext .vue,.js
	cd backend && source venv/bin/activate && black app/

# 清理临时文件
clean:
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/app/**/__pycache__
	rm -rf frontend/dist
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
