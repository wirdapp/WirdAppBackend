# Use an argument for Python version
ARG PYTHON_VERSION=3.9.6

###########
# BUILDER #
###########

# Use a smaller base image for the builder stage
FROM python:${PYTHON_VERSION}-slim as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        automake \
        g++ \
        postgresql \
        gcc \
        python3-dev \
        musl-dev \
        netcat \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install --no-cache-dir wheel

# Separate the copying of requirements and installing dependencies
COPY requirements.txt .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########

# Use a smaller base image for the final stage
FROM python:${PYTHON_VERSION}-slim

RUN mkdir -p /home/app

RUN addgroup --system app && adduser --system --no-create-home --disabled-login --disabled-password app
RUN adduser app app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        libblas3 \
        libc6 \
        liblapack3 \
        gcc \
        python3-dev \
        python3-pip \
        cython3 \
        libpq-dev \
    && apt install -y netcat \
    && rm -rf /var/lib/apt/lists/*

RUN pip install "gunicorn==20.0.4" \
    && pip install psycopg2-binary

# Copy the wheels and install dependencies separately
COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install /wheels/*

RUN mkdir -p /var/log/gunicorn/ /var/run/gunicorn/ /var/log/wird_app/
RUN chown -R app:app /var/log/gunicorn/ /var/run/gunicorn/ /var/log/wird_app/

COPY . $APP_HOME

RUN chown -R app:app $APP_HOME
RUN chmod +x $APP_HOME/start-server.sh

USER app
