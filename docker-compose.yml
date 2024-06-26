version: '3.8'

services:
  postgres:
    image: ghcr.io/your-username/microservices-repo-postgres:latest
    environment:
      POSTGRES_PASSWORD: yourpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  customer:
    image: ghcr.io/your-username/microservices-repo-customer:latest
    ports:
      - "8001:5000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgres://postgres:yourpassword@postgres:5432/yourdatabase

  venue:
    image: ghcr.io/your-username/microservices-repo-venue:latest
    ports:
      - "8002:5000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgres://postgres:yourpassword@postgres:5432/yourdatabase

  super_admin:
    image: ghcr.io/your-username/microservices-repo-super_admin:latest
    ports:
      - "8003:5000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgres://postgres:yourpassword@postgres:5432/yourdatabase

volumes:
  postgres_data:
