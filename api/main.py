import uvicorn
from dotenv import load_dotenv

def main():
    """Run the FastAPI application."""
    load_dotenv()
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)

if __name__ == "__main__":
    main()