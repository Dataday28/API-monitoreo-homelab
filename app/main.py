from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.websockets import router as ws_router

app = FastAPI(title="Project Sentinel API")

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    
)

app.include_router(ws_router)

@app.get("/")
async def root():
    return {"message": "OK"}