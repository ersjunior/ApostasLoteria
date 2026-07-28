from fastapi import FastAPI

from api.routes import combinations, dataset, verify

app = FastAPI()

app.include_router(verify.router, prefix="/verify")
app.include_router(combinations.router, prefix="/combinations")
app.include_router(dataset.router, prefix="/dataset")
