from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from splitio import get_factory
from config.split_config import SPLIT_API_KEY, USER_ID
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for Split client
split_factory = None
split_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Split client on startup
    global split_factory, split_client
    
    try:
        # Initialize Split factory with correct configuration
        split_factory = get_factory(SPLIT_API_KEY)
        
        # Get Split client instance
        split_client = split_factory.client()
        split_factory.block_until_ready(5)
        logger.info("Split client initialized successfully")
        
        yield
    except Exception as e:
        logger.error(f"Failed to initialize Split client: {e}")
        raise
    finally:
        # Cleanup on shutdown
        if split_client:
            try:
                split_client.destroy()
                logger.info("Split client destroyed successfully")
            except Exception as e:
                logger.error(f"Failed to destroy Split client: {e}")

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home(request: Request):
    try:
        if not split_client:
            raise RuntimeError("Split client not initialized")

        # Get treatment for feature flag
        treatment = split_client.get_treatment(
            USER_ID,
            "new_feature_flag"
        )
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "treatment": treatment,
                "is_feature_enabled": treatment == "on"
            }
        )
    except Exception as e:
        logger.error(f"Error getting treatment: {e}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "treatment": "control",
                "is_feature_enabled": False,
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)