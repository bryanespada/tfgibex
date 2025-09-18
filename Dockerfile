FROM python:3.12.1-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Quitar las ENV hardcodeadas - usar .env en su lugar
ENV SERVER_PRODUCTION=yes
#ENV GOOGLE_OAUTH_CLIENT_ID=os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '')
#ENV GOOGLE_OAUTH_CLIENT_SECRET=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', '')
WORKDIR /app

COPY ./requirements.txt /app/

RUN apt-get update
# Instalación de MariaDB
RUN curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | bash 
RUN apt-get update
RUN apt-get install -y mariadb-client
RUN apt-get install -y libmariadb-dev-compat
RUN apt-get install -y libmariadb-dev
RUN apt-get install -y gcc 
RUN apt-get install -y build-essential 
RUN apt-get install -y python3-dev 
RUN apt-get install -y musl-dev 
RUN apt-get install -y python3-apt 
RUN apt-get install -y python3-pycurl
RUN apt-get install -y libffi-dev
RUN apt-get install -y pkg-config

RUN pip install --upgrade pip wheel
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Dar permisos al entrypoint
RUN chmod +x entrypoint.sh

EXPOSE 8000

# Usar el entrypoint desde /app (no desde /docker-entrypoint.sh)
ENTRYPOINT ["./entrypoint.sh"]