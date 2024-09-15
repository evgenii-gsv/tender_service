# Tender Service

## How to run the service
1. Go to the root folder of the project and build the docker image.
```
docker build -t tender_service_image .
```
2. Set the environment variables (you can put them in the `.env` file).
3. Run the docker container with the environment variables.
```
docker run -p 8080:8080 --env-file .env --name tender_service tender_service_image 
```

## Environment variables
`SERVER_ADDRESS` - address and port of the server (0.0.0.0:8080 by default)

`POSTGRES_CONN` - URL to connect to PostgeSQL database: postgres://{username}:{password}@{host}:{5432}/{dbname}

`POSTGRES_JDBC_URL` - JDBC to connect to PostgeSQL database: jdbc:postgresql://{host}:{port}/{dbname}

`POSTGRES_USERNAME` - username to connect to PostgeSQL database

`POSTGRES_PASSWORD` - password to connect to PostgeSQL database

`POSTGRES_HOST` - host to connect to PostgeSQL database (e.g. localhost)

`POSTGRES_PORT` - port to connect to PostgeSQL database (e.g. 5432)

`POSTGRES_DATABASE` - the name of the database that will be user by server
