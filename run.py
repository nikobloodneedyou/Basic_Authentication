# Windows - venv\Scripts\activate, MacOS - source venv/bin/activate
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)