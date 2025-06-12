FROM python:3.10-slim

WORKDIR /app

# Install pipx and uv
RUN pip install pipx && pipx install uv

COPY uv.lock pyproject.toml ./

RUN pipx run uv sync --frozen --no-dev

COPY . .

RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["pipx", "run", "uv", "run", "fastapi", "run", "/app/api/main.py", "--host", "0.0.0.0", "--port", "8080"]