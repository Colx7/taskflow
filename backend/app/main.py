"""主应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.routers import auth, users, categories, tags, tasks, ai, stats, weekly_report
import traceback


class DisableTrailingSlashRedirect(BaseHTTPMiddleware):
    """拦截 POST 请求的 307 重定向，避免尾部斜杠问题"""
    async def dispatch(self, request, call_next):
        if request.method == "POST":
            response = await call_next(request)
            if response.status_code == 307:
                return JSONResponse(status_code=404, content={"detail": "找不到该页面"})
            return response
        return await call_next(request)


app = FastAPI(
    title="📋 TaskFlow 任务管理系统",
    description=(
        "AI 智能任务管理系统后端 API。\n\n"
        "### 使用步骤\n\n"
        "1. **注册** — 调用 `/api/auth/register` 创建账号\n"
        "2. **登录** — 调用 `/api/auth/login` 获取 Token\n"
        "3. **复制 Token** — 点击上方 'Authorize' 按钮粘贴 Token\n"
        "4. **调用接口** — 所有接口都已就绪，点击 Try it out → Execute\n\n"
        "### 接口说明\n\n"
        "| 分组 | 说明 |\n"
        "|------|------|\n"
        "| 🔐 认证 | 注册、登录、获取用户信息 |\n"
        "| 📂 分类 | 任务分类的增删改查 |\n"
        "| 🏷️ 标签 | 标签管理 |\n"
        "| ✅ 任务 | 任务的增删改查、批量操作 |\n"
        "| 🤖 AI | 智能分类、周报生成 |\n"
        "| 📊 统计 | 仪表盘数据、趋势图、分类分布 |\n"
    ),
    version="1.0.0",
    redirect_slashes=False,
    docs_url="/docs",       # Swagger UI 地址
    redoc_url="/redoc",     # ReDoc 地址（另一种风格）
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理 — 返回详细错误信息"""
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误: {exc}"},
    )


@app.get("/", response_class=HTMLResponse)
async def homepage():
    """欢迎页面"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>TaskFlow API</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; margin: 0; padding: 40px; color: #333; }
            .container { max-width: 800px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
            h1 { color: #409EFF; margin: 0 0 8px; }
            .subtitle { color: #909399; margin-bottom: 30px; }
            .section { margin: 24px 0; }
            .section h2 { font-size: 18px; color: #303133; border-left: 4px solid #409EFF; padding-left: 12px; }
            .step { display: flex; align-items: flex-start; margin: 12px 0; }
            .step-num { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: #409EFF; color: #fff; border-radius: 50%; font-size: 14px; margin-right: 12px; flex-shrink: 0; }
            .step-text { padding-top: 2px; }
            .step-text code { background: #f0f2f5; padding: 2px 8px; border-radius: 4px; font-size: 14px; color: #409EFF; }
            .links { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 24px; }
            .links a { display: inline-block; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-size: 15px; transition: all 0.2s; }
            .links a.primary { background: #409EFF; color: #fff; }
            .links a.primary:hover { background: #66b1ff; }
            .links a.secondary { background: #f0f2f5; color: #606266; }
            .links a.secondary:hover { background: #e4e7ed; }
            .tag { display: inline-block; padding: 2px 10px; border-radius: 4px; font-size: 12px; margin-right: 6px; }
            .tag.auth { background: #f0f9eb; color: #67c23a; }
            .tag.task { background: #ecf5ff; color: #409eff; }
            .tag.ai { background: #fdf6ec; color: #e6a23c; }
            .tag.stats { background: #f4f4f5; color: #909399; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📋 TaskFlow 任务管理系统</h1>
            <div class="subtitle">AI 智能任务管理 · 自动分类 · 智能优先级 · 周报生成</div>

            <div class="section">
                <h2>📖 如何使用</h2>
                <div class="step">
                    <span class="step-num">1</span>
                    <div class="step-text">
                        <strong>注册账号</strong> — 访问 <code>/docs</code>，找到「认证」分组，POST /api/auth/register
                    </div>
                </div>
                <div class="step">
                    <span class="step-num">2</span>
                    <div class="step-text">
                        <strong>登录获取 Token</strong> — POST /api/auth/login，复制返回的 token
                    </div>
                </div>
                <div class="step">
                    <span class="step-num">3</span>
                    <div class="step-text">
                        <strong>授权</strong> — 点击右上角 <code>Authorize</code> 按钮，粘贴 Token
                    </div>
                </div>
                <div class="step">
                    <span class="step-num">4</span>
                    <div class="step-text">
                        <strong>开始调用</strong> — 点击任意接口 → Try it out → Execute
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🔗 快速链接</h2>
                <div class="links">
                    <a href="/docs" class="primary">📘 Swagger UI</a>
                    <a href="/redoc" class="secondary">📗 ReDoc</a>
                </div>
            </div>

            <div class="section">
                <h2>📦 接口分组</h2>
                <div>
                    <span class="tag auth">🔐 认证</span>
                    <span class="tag task">✅ 任务</span>
                    <span class="tag ai">🤖 AI</span>
                    <span class="tag stats">📊 统计</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


app.add_middleware(DisableTrailingSlashRedirect)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(tasks.router)
app.include_router(ai.router)
app.include_router(stats.router)
app.include_router(weekly_report.router)
