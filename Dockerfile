FROM python:3.10-slim
WORKDIR /app
RUN apt-get update -y
RUN /usr/local/bin/python -m pip install --upgrade pip
COPY . .
RUN pip3 install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["python3","api.py", "--server.port=8501", "--server.address=0.0.0.0"]