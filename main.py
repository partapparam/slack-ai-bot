import uvicorn
from backend.server import api

if __name__ == "__main__":
    uvicorn.run(api, host='localhost', port=8000, reload=True)
    