from fastapi import FastAPI
import uvicorn


app = FastAPI()


@app.get("/getindex")
async def getindex():
    return {"data" : "this is a index page"}





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9800)