# Docker (Compose)

We use Docker to configure all of the services that we need to in order to run the data pipeline.

## Overview

The first key component of this is our Postgres instance. __Please note that I would not necessarily
recommend using Postgres inside a container in an enterprise production setting - this is a pet 
project after all!__

You can see full configurations for the database inside `docker-compose.yml` but, let's first zoom 
in on the database service itself,

```yaml
services:

  db:
    image: postgres
    container_name: publications-db
    restart: always
    user: postgres
    secrets:
      - db-password
    volumes:
      - publications-db-data:/var/lib/postgresql/data
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - backend
    environment:
      - POSTGRES_DB=publications
      - POSTGRES_PASSWORD_FILE=/run/secrets/db-password
    ports:
      - 5432:5432
    healthcheck:
      test: [ "CMD", "pg_isready" ]
      interval: 10s
      timeout: 5s
      retries: 5
  
  ...

volumes:
  db-data:
  ...

secrets:
  db-name:
    file: env/DB_NAME.txt
  db-password:
    file: env/DB_PWD.txt
  ...

```
If you would like a more comprehensive understanding of what all of these name-value pairs mean
the official Docker documentation (https://docs.docker.com/reference/compose-file/services/) is 
really quite good.

Note that most tags (and most certainly any confidential information such as passwords) are 
compiled as Docker secrets: this is intentional as we (obviously) do not want to expose information
like this to another third party. Data security is not my specialism but, in practice, with the above
in place, the only way a nefarious third party could gain control of these resources would be if
they were able to gain control of the deployment host and/or the containers on the host which I have 
done everything in my power to 'secure' properly.

In addition to the database container, another container is incorporated into the system to enable
administrative control over the database via the GUI PgAdmin (image: `dpage/pgadmin4`). You can
see the full configuration inside `docker-compose.yml`.

## Ports

You can spin up the services using `docker compose up -d`. Once this has been done, you can run
`docker ps` inside your terminal instance to see high-level metadata on each container. 

Most of the information displayed is fairly intuitive, but one part which might confuse somebody
is the port mappings. For instance, on spinning up the admin container, you will see something like
this,

```
443/tcp, 0.0.0.0:8888->80/tcp
```

To decode what this means: the _container_ exposes ports 443 and 80 (internally) by default. Port
80, however, has been mapped (by us in our `docker-compose.yml`) to port 8888 on our host machine.

Port 80 is special because it is typically used by web servers to listen for HTTP traffic. In other 
words, the `pgadmin4` image includes a web server (such as Apache, Nginx, or a lightweight built-in 
server) to handle HTTP (port 80) and HTTPS (port 443) traffic.

In effect, this means that if we type `localhost:8888` into our browser, this request will be redirected to port 80 on the container and we, in turn, will be redirected to the administrative GUI so that we can inspect our Postgres database. 

You can test all of this by running the Linux command,

`curl http://localhost:8888`