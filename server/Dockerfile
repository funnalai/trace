FROM python:3.10.1 as requirements-stage

WORKDIR /app

# Install Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN python -m pip install --upgrade pip

RUN pip install poetry

# Copy contents of server folder
COPY . /app

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN pip install --upgrade -r /app/requirements.txt

# Note, this is better in production since our image has less bloat
# But, this line makes the time to build our Docker image much longer
# on subsequent builds (since Docker doesn't have the cache baked into this layer)
# RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

RUN make setup

EXPOSE 80

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]