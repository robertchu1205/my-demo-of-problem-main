FROM python:3.9-alpine
COPY . /
WORKDIR /

RUN pip3 install -r requirement.txt
EXPOSE 3000

ENTRYPOINT ["python", "/server.py"]
# ENTRYPOINT ["python3", "-m", "swagger_server"]