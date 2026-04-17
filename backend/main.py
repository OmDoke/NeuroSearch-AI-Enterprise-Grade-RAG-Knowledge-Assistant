from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.routes import chat, ingest

app = FastAPI(title="NeuroSearch AI RAG API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://omportfolio-umber.vercel.app",
        "https://neurosearch-ui.onrender.com",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler — ensures CORS headers are ALWAYS present,
# even when the route crashes with a 500 error.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*"},
    )

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingest"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "NeuroSearch API is running"}
