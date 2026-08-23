FROM python:3.11-slim

WORKDIR /app

# Create a non-root user with UID 1000 for Hugging Face Spaces
RUN useradd -m -u 1000 user && \
    mkdir -p /app/uploads /tmp/uploads && \
    chown -R user:user /app /tmp/uploads

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

USER user

EXPOSE 7860 8888 10000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
