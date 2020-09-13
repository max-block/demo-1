FROM python:3.9.0 as builder

ARG PYPI_INDEX=https://pypi.org/simple
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -qU pip wheel
COPY requirements.txt /mnt/
RUN pip install -qr /mnt/requirements.txt -i $PYPI_INDEX
COPY dist/app-*.whl /mnt/dist/
RUN pip install -q /mnt/dist/* && pip check


FROM python:3.9.0-slim as app

# exposed port is required for docker nginx companion
EXPOSE 3000
ARG EXTRA_PACKAGES=''
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN apt update && apt-get install -y --no-install-recommends netcat $EXTRA_PACKAGES
COPY --from=builder /opt/venv /opt/venv
COPY scripts/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
