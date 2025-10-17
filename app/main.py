import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gradio.routes import mount_gradio_app

from app.api.endpoints import api_router
from app.ui import build_interface

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("API_TITLE", "Futurisys ML API"),
    description=os.getenv("API_DESCRIPTION", "Simple ML model deployment API"),
    version=os.getenv("API_VERSION", "1.0.0"),
)

# === Middleware CORS (utile si tu appelles ton API depuis le front) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ à restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v1")

# Montage de Gradio sur /ui
demo = build_interface()
app = mount_gradio_app(app, demo, path="/ui")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000))
    )
