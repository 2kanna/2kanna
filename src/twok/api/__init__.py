from fastapi import FastAPI
from datetime import datetime

from twok.api.routers import board, post, search, user
from twok.database.session import Session
from twok.database import schemas


tags_metadata = [
    {
        "name": "Post",
        "description": "Post.",
    },
    {
        "name": "Board",
        "description": "Board.",
    },
    {
        "name": "Search",
        "description": "Search.",
    },
    {
        "name": "User",
        "description": "User.",
    },
    {
        "name": "Health",
        "description": "Health Checks.",
    },
]

app = FastAPI(
    title="2K API",
    description="...",
    version="0.0.1",
    openapi_tags=tags_metadata,
)

app.include_router(post.post_router)
app.include_router(board.board_router)
app.include_router(search.search_router)
app.include_router(user.user_router)


@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


@app.on_event("startup")
async def startup():
    print("Starting up...")
    app.state.db_pool = Session()


@app.on_event("shutdown")
async def shutdown():
    app.state.db_pool.close()


# Health check endpoint
@app.get("/health", tags=["Health"], response_model=schemas.HealthCheckResponse)
async def health_check():
    return {"status": "OK", "time": str(datetime.utcnow())}
