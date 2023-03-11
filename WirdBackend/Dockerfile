###########
# BUILDER #
###########

# pull official base image
FROM python:3.9.6-slim as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y  && apt-get upgrade -y \
   automake \
   g++ \
   postgresql \
   gcc \
   python3-dev \
   musl-dev \
   netcat \
   libpq-dev \
#   jpeg-dev \
#   zlib-dev \
#    libgcc \
#    libstdc++ \
   && rm -rf /var/lib/apt/lists/*

#RUN apt-get update
#RUN apt-get -qq -y install curl
#RUN apt-get install -y automake g++ postgres-server-dev-all gcc python3-dev musl-dev jpeg-dev zlib-dev
#RUN apt-get install -y libgcc libstdc++
# lint
RUN pip install --upgrade pip
#RUN pip install flake8==3.9.2
COPY . .
#RUN flake8 --ignore=E501,F401 .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.9.6-slim
# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup --system app && adduser --system --no-create-home --disabled-login --disabled-password app
RUN adduser app app 

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install -y  && apt-get upgrade -y \
build-essential libssl-dev libffi-dev libblas3 libc6 \
 liblapack3 gcc python3-dev python3-pip cython3 libpq-dev
RUN apt install -y netcat
RUN pip install "gunicorn==20.0.4"
RUN pip install psycopg2-binary
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install /wheels/*

# copy entrypoint.prod.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

#Gunicorn
RUN mkdir -p /var/log/gunicorn/
RUN mkdir -p /var/run/gunicorn/
RUN chown -cR app:app /var/log/gunicorn/
RUN chown -cR app:app /var/run/gunicorn/
COPY ./gunicorn .

#Log files
RUN mkdir -p /var/log/wird_app/
RUN chown -cR app:app /var/log/wird_app/

#copy start serer
COPY ./start_server.sh .
RUN chmod +x  $APP_HOME/start_server.sh

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.prod.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
