# Metro Mondego Transit System

A full-stack database-centric system for managing an urban transit network — built with **PostgreSQL** and a **Python REST API**, designed and implemented as part of the Databases course at FCTUC (University of Coimbra), 2025/2026.

---

## Overview

Metro Mondego is a surface metro system serving the Coimbra region with three fixed lines:

| Line | Route |
|------|-------|
| Line 1 | Portagem → Hospital |
| Line 2 | Portagem → Estação B |
| Line 3 | Portagem → Miranda do Corvo → Lousã (Serpins) |

The system supports ticket management, wallet top-ups, real-time trip scheduling, fare promotions, and admin analytics — all exposed through a RESTful API and backed by a transactional PostgreSQL database.

---

## Project Structure

```
.
├── data-api.py               # Main REST API (Python)
├── createtable.sql           # Database schema (DDL)
├── insertdata.sql            # Sample data (DML)
├── metro_postman_collection.json  # Postman test collection
├── diagrama_conceptual_final_v3.json  # ONDA conceptual model (JSON export)
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Database | PostgreSQL |
| API Language | Python (psycopg3) |
| Authentication | JWT (JSON Web Tokens) |
| API Testing | Postman |
| Modelling | ONDA (ER Diagram) |
| Containerization | Docker |

---

## Database Schema

The relational schema includes **15+ interconnected tables**:

- `pessoa` — base entity for all users (customers and admins)
- `cliente` — customer-specific data (wallet, NIF, phone)
- `administrador` — admin accounts (regular + super)
- `linha` — metro lines with schedule parameters
- `paragem` — stations
- `trajeto` — ordered sequence of stations per line and direction
- `viagem` — concrete trip instances (departure time, capacity, delay)
- `bilhete` — tickets/passes purchased by customers
- `tipo_bilhete` — ticket types (single trip, daily, monthly, student, senior)
- `historico_preco` — historical fare prices over time
- `validacao` — ticket usage/validation records
- `promocao` — discount rules per line and ticket type
- `aviso` / `aviso_cliente` — admin notices broadcast to customers
- `carregamento` — wallet top-up records
- `interrupcao_linha` — temporary line closures

---

## Authentication & Roles

The system uses **JWT-based authentication** with three role levels:

| Role | Permissions |
|------|------------|
| **Super Admin** | Full access; creates/revokes admin accounts |
| **Admin** | Manages fares, promotions, notices, line operations; views analytics |
| **Customer** | Registers, tops up wallet, buys/uses/cancels tickets, reads notices |

Every endpoint (except login) requires a Bearer token in the `Authorization` header.

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/dbproj/user` | User login — returns JWT token |

### Super Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| PUT | `/dbproj/register/admin` | Create a new administrator |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/dbproj/register/customer` | Register a new customer |
| PUT | `/dbproj/line_operation/{line_id}` | Update line schedule/capacity |
| PUT | `/dbproj/fares/{fare_id}` | Update fare price with effective date |
| POST | `/dbproj/notices/broadcast` | Broadcast notice to all customers |
| POST | `/dbproj/promotions` | Create a discount/promotion rule |

### Customer
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dbproj/lines_next` | List all lines and next departures |
| POST | `/dbproj/wallet/topup` | Add funds to wallet |
| POST | `/dbproj/purchase` | Purchase a ticket or pass |
| POST | `/dbproj/ticket/use/{ticket_id}` | Validate/use a ticket at a station |

### Analytics (Admin)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dbproj/report/demand` | Peak and low demand periods per line |
| GET | `/dbproj/report/top_spenders` | Top spending customers per line (last 30 days) |
| GET | `/dbproj/report/monthly` | Monthly active and repeat customers per line |

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Docker (optional)
- Postman

### 1. Clone the repository

```bash
git clone https://github.com/akcelgraca/Data-Bases---Metro-Mondego-System.git
cd Data-Bases---Metro-Mondego-System
```

### 2. Install Python dependencies

```bash
pip install psycopg flask pyjwt
```

### 3. Set up the database

```bash
psql -U postgres -c "CREATE DATABASE metromondego;"
psql -U postgres -d metromondego -f createtable.sql
psql -U postgres -d metromondego -f insertdata.sql
```

### 4. Run the API

```bash
python data-api.py
```

The server will start at `http://localhost:8080`.

### 5. Test with Postman

Import `metro_postman_collection.json` into Postman and run the requests in order (authentication first to obtain the JWT token).

---

## Ticket Types

| Type | Description |
|------|-------------|
| `single_trip` | One-way trip on a specific date |
| `daily` | Unlimited travel for 24 hours |
| `monthly_pass` | 30-day unlimited pass |
| `monthly_student` | 30-day student pass (discounted) |
| `monthly_senior` | 30-day senior pass (discounted) |

---

## Key Technical Highlights

- **Transactional Integrity** — Explicit transaction handling with concurrency conflict mitigation (isolation levels, locking strategies)
- **Trigger-based automation** — Wallet deduction on ticket purchase handled via PostgreSQL triggers
- **Price history tracking** — Full audit trail of fare changes over time
- **Single-query analytics** — Complex reporting endpoints resolved in a single SQL query (no post-processing in Python)
- **Role-based access control** — All endpoints validate JWT claims before processing
- **Normalized schema** — Designed following relational normalization principles to avoid redundancy and ensure integrity

---

## Authors

- **Akcel Graça** — [LinkedIn](https://www.linkedin.com/in/akcelgraça) · [GitHub](https://github.com/akcelgraca)

*Databases Course — Licenciatura em Engenharia Informática, FCTUC, University of Coimbra*
*2025/2026*

---

## License

This project was developed for academic purposes at the University of Coimbra.