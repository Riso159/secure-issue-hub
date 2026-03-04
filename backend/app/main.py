from fastapi import FastAPI

app = FastAPI(title="SecureIssueHub API")


@app.get("/")
def read_root():
    return {"message": "API is running"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
