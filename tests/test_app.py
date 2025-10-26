from fastapi import FastAPI

app = FastAPI(title="DuckLearn API")

@app.get("/")
def root():
    return {"message": "Hello from DuckLearn!"}