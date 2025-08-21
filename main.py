from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Welcome to Python FastAPI World!"}

@app.get("/health", status_code=200, response_description="Health Check")
def read_health():
    return {"status": "OK", "message": "Service is running"}

@app.get("/first", status_code=200, response_description="Health Check")
def read_health():
    return {"status": "OK", "message": "Service1 is running"}


