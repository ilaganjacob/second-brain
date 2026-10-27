from fastapi import FastAPI

app = FastAPI(title="Second Brain")


@app.get("/api/health")
def health() -> dict[str, bool]:
    return {"ok": True}
