PROJECT_NAME = $(shell grep APP_NAME .env | cut -d '=' -f 2-)
VERSION = $(shell python3 setup.py --version | tr '+' '-')
PYPI_INDEX = $(shell grep PYPI_INDEX .env | cut -d '=' -f2)
EXTRA_PACKAGES = $(shell grep EXTRA_PACKAGES .env | cut -d '=' -f2)
DOCKER_REGISTRY = $(shell grep DOCKER_REGISTRY .env | cut -d '=' -f2)
PROJECT_IMAGE ?= $(DOCKER_REGISTRY)/$(PROJECT_NAME)

.DEFAULT_GOAL := dev

clean:
	rm -rf .pytest_cache build dist *.egg-info


dist: clean
	python3 setup.py sdist bdist_wheel


docker: dist
	docker build --build-arg PYPI_INDEX=$(PYPI_INDEX) --build-arg EXTRA_PACKAGES=$(EXTRA_PACKAGES) --target=app -t $(PROJECT_NAME):$(VERSION) .
	docker tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest


docker-compose: dist
	docker-compose up --build


docker-no-cache: dist
	docker build --build-arg PYPI_INDEX=$(PYPI_INDEX) --build-arg EXTRA_PACKAGES=$(EXTRA_PACKAGES) --target=app -t $(PROJECT_NAME):$(VERSION) --no-cache .
	docker tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest


upload: docker
	docker tag $(PROJECT_NAME):$(VERSION) $(PROJECT_IMAGE):$(VERSION)
	docker push $(PROJECT_IMAGE):$(VERSION)


update: upload
	cd ansible;	ansible-playbook -i hosts.yml --extra-vars="playbook_action=update app_version=$(VERSION)" playbook.yml


host:
	cd ansible;	ansible-playbook -i hosts.yml --extra-vars="playbook_action=host" playbook.yml


dev:
	uvicorn --port 3000 --log-level warning app.main:app

gunicorn:
	gunicorn -b 0.0.0.0:3000 --timeout 999 --threads 12 -k uvicorn.workers.UvicornWorker app.main:app
