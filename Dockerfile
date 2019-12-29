FROM python:3.5

COPY . /app
WORKDIR /app

RUN pip3 install -r requirement.txt

EXPOSE 5000

ENTRYPOINT ["python3.5"]
CMD ["app.py"]