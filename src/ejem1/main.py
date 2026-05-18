"""Punto de entrada FastAPI; expone app y el comando CLI ejem1."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ejem1.database import Base, engine
from ejem1.routers import authors, books


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Biblioteca API", version="1.0.0", lifespan=lifespan)

app.include_router(authors.router)
app.include_router(books.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Reformatea los errores de validación Pydantic al formato uniforme."""
    details = []
    for error in exc.errors():
        loc_parts = [str(part) for part in error["loc"] if part != "body"]
        field = ".".join(loc_parts) if loc_parts else "request"
        details.append({"field": field, "issue": error["msg"]})
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "One or more validation errors occurred.",
                "details": details,
            }
        },
    )


_HTTP_CODE_MAP = {
    400: "BAD_REQUEST",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_ERROR",
}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Reformatea las HTTPException al formato uniforme de error."""
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": _HTTP_CODE_MAP.get(exc.status_code, "UNKNOWN"),
                "message": str(exc.detail),
                "details": [],
            }
        },
    )


def main() -> None:
    """Arranca el servidor de desarrollo con uvicorn."""
    import uvicorn

    uvicorn.run("ejem1.main:app", host="0.0.0.0", port=8000, reload=True)
