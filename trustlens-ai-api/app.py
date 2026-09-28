from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="TrustLens AI API")

app.include_router(router)
