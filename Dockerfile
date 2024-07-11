FROM python:3.9-slim

# Setting working directory
WORKDIR /app

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


# Expose necessary ports
#EXPOSE 8000 8001 8002 8003

# Command to run the services
#CMD ["sh", "-c", "python /app/customer_app/app_cusotmer.py & python /app/vendor_app/app_vendor.py & python /app/super_admin/admin_app.py & python /app/cron/run_cron.py & tail -f /dev/null"]
