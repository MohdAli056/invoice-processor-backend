import uvicorn
from app import app

if __name__ == "__main__":
    # Production configuration for cloud deployment
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.environ.get("PORT", 8000)),
        log_level="info"
    )
