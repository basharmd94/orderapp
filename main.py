from fastapi import FastAPI
import uvicorn
from routers import opord_route

app = FastAPI()

app.include_router(opord_route.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9800)
