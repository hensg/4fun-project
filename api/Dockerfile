FROM python:3.6

EXPOSE 8000

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./app workdir/app
WORKDIR workdir

CMD ["gunicorn", "--workers", "8", "-b", "0.0.0.0:8000", "app.app:get_app()"]
