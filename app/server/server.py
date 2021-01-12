import traceback
from pathlib import Path
from typing import Callable

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import APIKey
from fastapi.openapi.utils import get_openapi
from fastapi.security import APIKeyCookie, APIKeyHeader, APIKeyQuery
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_403_FORBIDDEN

from app.core.core import Core
from app.core.errors import UserError
from app.server.jinja import configure_jinja
from app.server.routers import data_router, system_router, telegram_router, ui_router, worker_router
from app.telegram import Telegram


class Server:
    api_key_name = "access_token"

    key_query = Security(APIKeyQuery(name=api_key_name, auto_error=False))
    key_header = Security(APIKeyHeader(name=api_key_name, auto_error=False))
    key_cookie = Security(APIKeyCookie(name=api_key_name, auto_error=False))

    def __init__(self, core: Core, telegram: Telegram):
        self.core = core
        self.telegram = telegram
        self.app = FastAPI(
            title=core.config.app_name,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
            openapi_tags=core.config.tags_metadata,
        )
        self.templates = configure_jinja(core)
        self._configure_app()
        self._configure_openapi()
        self._configure_routers()
        telegram.start()

    def get_app(self) -> FastAPI:
        return self.app

    def _configure_routers(self):
        self.app.include_router(
            worker_router.init(self.core),
            prefix="/api/workers",
            dependencies=[Depends(self._get_api_key())],
            tags=["workers"],
        )
        self.app.include_router(
            data_router.init(self.core),
            prefix="/api/data",
            dependencies=[Depends(self._get_api_key())],
            tags=["data"],
        )
        self.app.include_router(
            system_router.init(self.core),
            prefix="/api/system",
            dependencies=[Depends(self._get_api_key())],
            tags=["system"],
        )
        self.app.include_router(
            telegram_router.init(self.telegram),
            prefix="/api/telegram",
            dependencies=[Depends(self._get_api_key())],
            tags=["telegram"],
        )
        self.app.include_router(
            ui_router.init(self.core, self.templates),
            prefix="/ui",
            dependencies=[Depends(self._get_api_key())],
            tags=["ui"],
        )

    def _configure_app(self):
        @self.app.exception_handler(Exception)
        async def exception_handler(_request: Request, err: Exception):
            code = getattr(err, "code", None)

            message = str(err)

            hide_stacktrace = isinstance(err, UserError)
            if code in [400, 401, 403, 404, 405]:
                hide_stacktrace = True

            if not hide_stacktrace:
                self.core.log.exception(err)
                message += "\n\n" + traceback.format_exc()

            if not self.core.config.debug:
                message = "error"

            return PlainTextResponse(message, status_code=500)

        @self.app.on_event("shutdown")
        def shutdown_server():
            self.telegram.stop()
            self.core.shutdown()

        current_dir = Path(__file__).parent.absolute()
        self.app.mount("/static", StaticFiles(directory=current_dir.joinpath("static")), name="static")

    def _configure_openapi(self):
        @self.app.get("/openapi.json", tags=["openapi"], include_in_schema=False)
        async def get_open_api_endpoint(_api_key: APIKey = Depends(self._get_api_key())):
            response = JSONResponse(
                get_openapi(
                    title=self.core.config.app_name,
                    version=self.core.config.version,
                    routes=self.app.routes,
                    tags=self.core.config.tags_metadata,
                ),
            )
            return response

        @self.app.get("/api", tags=["openapi"], include_in_schema=False)
        async def get_documentation(api_key: APIKey = Depends(self._get_api_key())):
            response = get_swagger_ui_html(openapi_url="/openapi.json", title=self.core.config.app_name)
            # noinspection PyTypeChecker
            response.set_cookie(
                self.api_key_name,
                value=api_key,
                domain=self.core.config.domain,
                httponly=True,
                max_age=60 * 60 * 24 * 30,
                expires=60 * 60 * 24 * 30,
            )
            return response

        @self.app.get("/logout", tags=["auth"])
        async def route_logout_and_remove_cookie():
            response = RedirectResponse(url="/")
            response.delete_cookie(self.api_key_name, domain=self.core.config.domain)
            return response

        @self.app.get("/")
        async def redirect_to_api():
            return RedirectResponse(url="/api")

    def _get_api_key(self) -> Callable:
        async def _get_api_key(
            query: str = Server.key_query,
            header: str = Server.key_header,
            cookie: str = Server.key_cookie,
        ):
            if query == self.core.config.access_token:
                return query
            elif header == self.core.config.access_token:
                return header
            elif cookie == self.core.config.access_token:
                return cookie
            else:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="access denied")

        return _get_api_key
