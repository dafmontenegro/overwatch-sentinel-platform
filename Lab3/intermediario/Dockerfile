FROM python:3.10-slim
WORKDIR /app
COPY app.py .
RUN pip install flask requests
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]