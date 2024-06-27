# Dockerfile

# Base image for Python services
FROM python:3.9-slim AS python-base

WORKDIR /app

# Environment variable to specify the microservice
ARG SERVICE
ENV SERVICE=${SERVICE}

# Copy the relevant service code and requirements based on the SERVICE argument
COPY ${SERVICE}/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ${SERVICE} /app

# Postgres service base image
FROM postgres:15 AS postgres-base

# Final stage to select the correct base image and run the service
FROM python-base AS final-stage
COPY --from=postgres-base /docker-entrypoint-initdb.d /docker-entrypoint-initdb.d

# Expose ports
EXPOSE 5000 5432

# Define the entrypoint for each service
CMD if [ "$SERVICE" = "customer" ]; then \
        python app.py; \
    elif [ "$SERVICE" = "venue" ]; then \
        python app.py; \
    elif [ "$SERVICE" = "super_admin" ]; then \
        python app.py; \
    elif [ "$SERVICE" = "postgres" ]; then \
        docker-entrypoint.sh postgres; \
    else \
        echo "Please specify a valid SERVICE environment variable"; \
        exit 1; \
    fi
