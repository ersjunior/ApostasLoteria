from fastapi import FastAPI

from api.routes import dataset, forecast, verify

app = FastAPI()

app.include_router(verify.router, prefix="/verify")
app.include_router(forecast.router, prefix="/forecast")
app.include_router(dataset.router, prefix="/dataset")
