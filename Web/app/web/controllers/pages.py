from fastapi import APIRouter, Request
from app.config import templates

pages_controller = APIRouter()

@pages_controller.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="pages/index.html")