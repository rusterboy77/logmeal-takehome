FROM python:3.11-slim
WORKDIR /app
# Add your requirements.txt and app code
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
EXPOSE 8000
CMD ["flask", "--app", "backend/app.py", "run", "--host=0.0.0.0", "--port=8000"]