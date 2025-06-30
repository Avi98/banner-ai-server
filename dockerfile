FROM python:3.12.3-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# System dependencies for Playwright
RUN apt-get update && apt-get install -y \
	wget \
	libnss3 \
	libxss1 \
	libasound2 \
	libatk-bridge2.0-0 \
	libgtk-3-0 \
	libdrm2 \
	libxcomposite1 \
	libxdamage1 \
	libxrandr2 \
	libgbm1 \
	libxkbcommon0 \
	libatspi2.0-0 \
	&& rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked

# Copy application code
COPY . .

# Install Playwright browsers
RUN /app/.venv/bin/playwright install chromium --with-deps

# Set PATH
ENV PATH="/app/.venv/bin:$PATH"

RUN ls -la /app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
