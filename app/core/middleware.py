import logging
import time

from fastapi import FastAPI, Request

app = FastAPI()

logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    process_time_ms = process_time * 1000

    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        process_time_ms,
    )

    return response
