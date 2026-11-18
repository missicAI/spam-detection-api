from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from du_doan import predict

app = FastAPI(
    title="Kiểm tra tin nhắn tiếng Việt", description="Gửi nội dung tiếng Việt để nhận dự đoán tin rác."
)


@app.exception_handler(RequestValidationError)
async def sai_dinh_dang(request, exc):
    return JSONResponse(
        status_code=422, content={"detail": "Bạn gửi nội dung dạng chữ trong trường noi_dung nhé."}
    )


class TinNhan(BaseModel):
    noi_dung: str = Field(description="Nội dung tin nhắn tiếng Việt")


@app.post("/predict", summary="Kiểm tra một tin nhắn")
def kiem_tra(tin: TinNhan):
    try:
        result = predict(tin.noi_dung)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from None
    return {"nhan": result, "ket_qua": "Có dấu hiệu tin rác" if result else "Chưa phát hiện dấu hiệu tin rác"}
