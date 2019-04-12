FROM python:3.7 as build

RUN pip install -U pip virtualenv \
 && virtualenv -p `which python3` /venv/

ENV PATH=/venv/bin/:$PATH

ADD ./requirements.pip /requirements.pip
RUN pip install -r /requirements.pip

FROM python:3.7

RUN apt-get update \
 && apt-get install --no-install-recommends -y ffmpeg \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid=1000 app \
 && useradd --uid=1000 --gid=1000 --system app
USER app

COPY --from=build --chown=app:app /venv/ /venv/
ENV PATH=/venv/bin/:$PATH

COPY --chown=app:app ./stt/ /app/stt/
WORKDIR /app

EXPOSE 8000

CMD python -m stt.app
