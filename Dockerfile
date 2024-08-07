FROM python:3.9-slim

# Setting working directory
WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

# Copy all microservices into the container
# COPY customer_app /app/customer_app
# COPY vendor_app /app/vendor_app
# COPY super_admin /app/super_admin
# COPY cron /app/cron

# Copy environment files
# COPY customer_app/.env /app/customer_app/.env
# COPY vendor_app/.env /app/vendor_app/.env
# COPY super_admin/.env /app/super_admin/.env
# COPY cron/.env /app/cron/.env
COPY . ./

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

ENV PYTHONPATH="/app"
