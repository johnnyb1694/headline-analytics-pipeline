# Configuration

## Naming

In order to create names for services that were memorable, I decided that rather than name 
everything in a generic fashion (e.g. `db`) I would tag every service with a prefix.

In the end, the selected prefix was 'Newton', named after the epoynmous mathematician and scientist
who - amongst many other things - was a highly influential figure in the realms of calculus and
theoretical physics.

Perhaps somebody else will come along soon and create another service called 'Leibniz' to rival
my own (I very much doubt it, since this is just a pet project but you never know!)

## Docker (Compose)

We use Docker to configure all of the services that we need to in order to run the data pipeline.

The first key component of this is our Postgres instance. __Please note that I would not necessarily
recommend using Postgres inside a container in an enterprise production setting - this is a pet 
project after all!__

You can see full configurations for the database inside `docker-compose.yml` but, let's first zoom 
in on the database service itself,

```yaml
services:

  db:
    image: postgres # the image we want to pull from Docker Hub
    container_name: newton-db # a convenient name for the container; alias for host name
    restart: always # if failure occurs, the container will always be restarted
    user: postgres # the user under which the container will 'run as'
    secrets: 
      - db-name # name of our database
      - db-password # password used to login to the database
    volumes:
      - db-data:/var/lib/postgresql/data # persists the *data* stored in the database on the host
      - ./src/db/init.sql:/docker-entrypoint-initdb.d/init.sql # initialises the raw data schema (for storing raw article data)
    environment:
      - POSTGRES_DB=/run/secrets/db-name
      - POSTGRES_PASSWORD_FILE=/run/secrets/db-password
    expose:
      - 5432:5432
    healthcheck: # a useful feature of Docker which defines 'when the service is ready'
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

## Digital Ocean

The entire application is deployed to a single server on Digital Ocean. At a larger scale, you
might decide to decompose the services (e.g. the database layer) across different servers but at 
this tiny scale, it didn't seem necessary to me!
