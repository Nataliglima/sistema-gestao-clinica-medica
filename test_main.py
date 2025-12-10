from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "funcionando"}

@app.get("/test")
def test():
    return {"teste": "ok"}
