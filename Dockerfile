# Use a base image with all necessary dependencies
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy all microservices into the container
COPY customer_app /app/customer_app
COPY vendor_app /app/vendor_app
COPY superadmin /app/superadmin
COPY cron_app /app/cron_app

# Copy environment files
COPY customer_app/.env /app/customer_app/.env
COPY vendor_app/.env /app/vendor_app/.env
COPY superadmin/.env /app/superadmin/.env
COPY cron_app/.env /app/cron_app/.env

# Install any necessary dependencies
# Assuming each microservice has its own requirements.txt
RUN pip install -r requirements.txt


# Expose necessary ports
EXPOSE 8000 8001 8002 8003

# Command to run the services
CMD ["sh", "-c", "python /app/customer_app/app.py & python /app/vendor_app/app.py & python /app/superadmin/app.py & python /app/cron_app/app.py & tail -f /dev/null"]
