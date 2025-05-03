# Dockerfile for the API to deploy on Hugging Face Spaces

FROM python:3.12-slim

WORKDIR /code

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Copy requirements and install dependencies
COPY --chown=user /requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# Copy API code and env example
COPY --chown=user ./ ./

# Set API to listen on port 7860 (required by Hugging Face)
ENV PORT=7860

# Start the application with correct path to main.py
CMD ["python", "app.py"]