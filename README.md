# Cosmetics Shop

## About

Cosmetics Shop is a full-featured e-commerce backend built with Django.

The project demonstrates:
- scalable architecture (service layer)
- async background processing (Celery)
- external payment integration (Monobank API)
- production-ready setup using Docker and Nginx

## Features

* User registration and authorization
* Product catalog
* Cart (add/delete/change quantity)
* Create orders? change order status
* Payment system integration (Monobank, sandbox)
* REST API (Django REST Framework)
* Background tasks (Celery)
* Custom admin panel for data management

## Tech Stack

* Python 3.11+
* Django
* Django REST Framework
* PostgreSQL
* Redis
* Celery
* Docker + Docker Compose
* Nginx

### Project Stats

- ~15 models
- ~40 API endpoints
- Test coverage: ~75%

## Quick Start

### 1. Clone project

```bash
git clone https://github.com/bayur-yuliya/cosmetics_shop
cd cosmetics_shop
```

### 2. Setting environment variables

```bash
cp .env.example .env
```

Write the data to `.env` (especially Monobank token and DB settings).

---

### 3. Running via Docker

```bash
docker-compose up --build
```

### 4. Create superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

---

### 5. Project launch

Open in browser:

```
http://localhost:8080
```

## Tests

Running tests:

```bash
pytest
```

Coverage includes:

* models
* services
* forms
* utilities

## Architecture

The project is built with a separation of responsibilities in mind:

* `accounts` — user management
* `cosmetics_shop` — core business logic (products, shopping cart, orders)
* `api` — REST API
* `staff` — admin logic

### Architecture Highlights

- Service layer separates business logic from Django models
- Celery handles async tasks:
  - order processing
  - payment status updates
- Redis is used for:
  - caching
  - message broker

## API Currently implemented endpoints:

- Order creation
- Product listing

### Example API

Create product:

POST /api/products/

```
{
    "id": 1,
    "name": "Product name",
    "price": "100.00",
    "stock": 0,
    "code": 1111111,
    "brand": {
        "id": 1,
        "name": "Name brand",
        "slug": "name-brand"
    },
    "group": {
        "id": 1,
        "name": "Name group",
        "slug": "name-group",
        "category": {
            "id": 1,
            "name": "Name category",
            "slug": "name-category"
        }
    },
    "is_active": true
}
```