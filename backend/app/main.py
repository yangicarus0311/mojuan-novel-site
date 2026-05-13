from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import auth, works, chapters, bookshelf, admin, payment, payment_webhook, admin_payment, highlights, reading, social, recommend

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="墨卷 API",
    description="网文小说平台后端API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(works.router, prefix="/api")
app.include_router(chapters.router, prefix="/api")
app.include_router(bookshelf.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(payment.router, prefix="/api")
app.include_router(payment_webhook.router, prefix="/api")
app.include_router(admin_payment.router, prefix="/api")
app.include_router(highlights.router, prefix="/api")
app.include_router(reading.router, prefix="/api")
app.include_router(social.router, prefix="/api")
app.include_router(recommend.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "欢迎使用墨卷 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
