import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api.endpoints import api_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title=os.getenv("API_TITLE", "Futurisys ML API"),
    description=os.getenv("API_DESCRIPTION", "Simple ML model deployment API"),
    version=os.getenv("API_VERSION", "1.0.0"),
)

app.include_router(api_router, prefix="/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8000))
    )
