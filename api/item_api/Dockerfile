FROM python:3.7
LABEL Name=line-echo-bot Version=0.0.1
WORKDIR /app
COPY ["requirements.txt", "/app/"]
RUN python3 -m pip install -r requirements.txt
ADD . /app
EXPOSE 31110
CMD ["gunicorn", "api:app", "--log-file=-", "--bind=0.0.0.0:31110"]
