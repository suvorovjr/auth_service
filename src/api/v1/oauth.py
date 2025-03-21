from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from src.api.v1.dependencies import YandexOAuthDep

oauth_router = APIRouter()


@oauth_router.get("/yandex/login")
async def login_with_yandex(oauth_service: YandexOAuthDep):
    url = await oauth_service.get_oauth_url()
    return RedirectResponse(url=url)


@oauth_router.get("/yandex/callback")
async def auth_callback(oauth_service: YandexOAuthDep, code: str = Query(...)):
    print(code)
    user_info = await oauth_service.get_user_info(code=code)
    return {"user_info": user_info}
