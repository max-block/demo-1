from fastapi import APIRouter, Depends, Request
from mb_commons import md
from mb_commons.mongo import make_query
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from wtforms import BooleanField, Form, IntegerField, SelectField, StringField
from wtforms.validators import URL

from app.core.core import Core
from app.core.models import DataStatus, WorkerCreate
from app.server.jinja import form_choices


async def get_form_data(request: Request):
    return await request.form()


class WorkersFilterForm(Form):
    name = StringField(default="")
    started = BooleanField()
    limit = IntegerField(default=100)


class WorkerCreateForm(Form):
    name = StringField()
    source = StringField(validators=[URL()])
    interval = IntegerField()


class DataFilterForm(Form):
    worker = StringField(default="")
    status = SelectField(choices=form_choices(DataStatus, title="status"), default="")
    limit = IntegerField(default=100)


def init(core: Core, templates: Jinja2Templates) -> APIRouter:
    router = APIRouter()

    @router.get("", response_class=HTMLResponse)
    def index_page(request: Request):
        return templates.TemplateResponse("index.j2", md(request))

    @router.get("/workers", response_class=HTMLResponse)
    def workers_page(request: Request):
        form = WorkersFilterForm(request.query_params)
        query = make_query(started=form.data["started"], name=form.data["name"])
        workers = core.db.worker.find(query, "-created_at", form.data["limit"])
        return templates.TemplateResponse("workers.j2", md(request, form, workers))

    @router.get("/create-worker")
    def create_worker_page(request: Request):
        form = WorkerCreateForm()
        return templates.TemplateResponse("create_worker.j2", md(request, form))

    @router.get("/data", response_class=HTMLResponse)
    def data_page(request: Request):
        form = DataFilterForm(request.query_params)
        query = make_query(worker=form.data["worker"], status=form.data["status"])
        data = core.db.data.find(query, "-created_at", form.data["limit"])
        return templates.TemplateResponse("data.j2", md(request, form, data))

    @router.post("/create-worker")
    def create_worker_action(form_data=Depends(get_form_data)):
        form = WorkerCreateForm(form_data)
        if form.validate():
            return core.worker_service.create(WorkerCreate(**form.data))
        else:
            return {"error": form.errors}

    return router
