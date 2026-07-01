from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.routes.router import router

app = FastAPI()

register_exception_handlers(app)

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Hello"}
