import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator

from spamguard.download import ROOT


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("text must contain a non-whitespace character")
        return value.strip()


class PredictionResponse(BaseModel):
    label: str
    spam_probability: float
    model_version: str


def create_app(model_path: Path | None = None):
    path = model_path or Path(os.getenv("MODEL_PATH", str(ROOT / "artifacts/spam_model.joblib")))

    @asynccontextmanager
    async def lifespan(app):
        app.state.bundle = joblib.load(path) if path.exists() else None
        yield

    app = FastAPI(
        title="SpamGuard API",
        version="1.0.0",
        description="English SMS classifier: TF-IDF + Logistic Regression. Train locally before serving.",
        lifespan=lifespan,
    )

    @app.get("/health")
    def health(request: Request):
        if request.app.state.bundle is None:
            raise HTTPException(503, "Model not found. Run python train.py before starting the API.")
        return {"status": "ready", "model_loaded": True}

    @app.post("/predict", response_model=PredictionResponse)
    def predict(payload: PredictionRequest, request: Request):
        bundle = request.app.state.bundle
        if bundle is None:
            raise HTTPException(503, "Model not found. Run python train.py before starting the API.")
        pipeline = bundle["pipeline"]
        index = list(pipeline.classes_).index("spam")
        probability = float(pipeline.predict_proba([payload.text])[0, index])
        label = str(pipeline.predict([payload.text])[0])
        return PredictionResponse(
            label=label, spam_probability=probability, model_version=bundle["metadata"]["created_at_utc"]
        )

    return app


app = create_app()
