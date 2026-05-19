# 1. Overview & Initial Database State

Based on the provided mock data (`db_mock_data/`), the Metro Mondego database initializes with a rich set of testing entities.

**Available Accounts for Testing:**

- **Super Admin:** `superadmin` / `hash_super`
- **Admin:** `admin1` / `hash_admin1`
- **Customers:**
    - `anacosta` (Wallet: €50.00) / `hash_ana`
    - `brunosilva` (Wallet: €20.00) / `hash_bruno`
    - `carlam` (Wallet: €100.00) / `hash_carla`

**Network Assets:**

- **Lines:**
    1. Portagem - Hospital
    2. Portagem - Estacao B
    3. Portagem - Miranda do Corvo - Lousa

# 2. Endpoint Testing Guide

### Endpoint 1: Authentication (Login)

- **Description:** Authenticates a user and returns a JWT token.
- **Method & URL:** `PUT http://localhost:8080/dbproj/user`
- **Headers:** `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "username": "superadmin",
    "password": "hash_super"
}
```

- **Expected Response:**

```json
{
    "status": 200,
    "results": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Endpoint 2: Add Administrator

- **Description:** Creates a new administrator. Requires Super Admin token.
- **Method & URL:** `PUT http://localhost:8080/dbproj/register/admin`
- **Headers:** `Authorization: Bearer <super_admin_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "name": "Novo Admin",
    "email": "newadmin@metromondego.pt",
    "password": "secret_password"
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "results": {
        "user_id": 8
    },
    "status": 200
}
```

### Endpoint 3: Add Customer

- **Description:** Creates a new customer. Requires Admin token.
- **Method & URL:** `POST http://localhost:8080/dbproj/register/customer`
- **Headers:** `Authorization: Bearer <admin_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "name": "Novo Cliente",
    "nif": "234567891",
    "telefone": "912345678",
    "email": "newcustomer@email.pt",
    "password": "secret_password"
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "results": {
        "user_id": 9
    },
    "status": 200
}
```

### Endpoint 4: Update Line Operation Settings

- **Description:** Updates time configurations and frequencies for a specific line. Admin access.
- **Method & URL:** `PUT http://localhost:8080/dbproj/line_operation/1`
- **Headers:** `Authorization: Bearer <admin_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "start_time": "06:30:00",
    "end_time": "23:00:00",
    "frequency_minutes": 15,
    "vehicle_capacity": 60
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "status": 200
}
```

### Endpoint 5: Update Fare Price

- **Description:** Adds a new entry into the price history for a given ticket type. Admin access.
- **Method & URL:** `PUT http://localhost:8080/dbproj/fares/1`
- **Headers:** `Authorization: Bearer <admin_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "price": 1.8,
    "effective_from": "2026-06-01"
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "status": 200
}
```

### Endpoint 6: Broadcast Notice

- **Description:** Broadcasts a global system notice to all customers. Admin access.
- **Method & URL:** `POST http://localhost:8080/dbproj/notices/broadcast`
- **Headers:** `Authorization: Bearer <admin_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "title": "System Update",
    "message": "We are updating our backend systems tonight."
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "status": 200
}
```

### Endpoint 7: Create Promotion

- **Description:** Inserts a discount promotion for a specific line and ticket type. Admin access.
- **Method & URL:** `POST http://localhost:8080/dbproj/promotions`
- **Headers:** `Authorization: Bearer <admin_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "name": "Spring Discount",
    "line_id": 1,
    "product_type": "single_trip",
    "discount_percent": 15,
    "start_date": "2026-05-20",
    "end_date": "2026-05-30"
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "results": {
        "promotion_id": 3
    },
    "status": 200
}
```

### Endpoint 8: List Lines and Next Departures

- **Description:** Retrieves real-time availability and estimations per line. Customer/Authenticated access.
- **Method & URL:** `GET http://localhost:8080/dbproj/lines_next`
- **Headers:** `Authorization: Bearer <customer_token>`
- **Request Body (JSON):** _None_
- **Expected Response:**

```json
{
    "errors": null,
    "results": [
        {
            "available_capacity": 50,
            "departure_time": "2026-05-19 08:00:00",
            "destination_terminal": "Estacao B",
            "estimated_delay_min": 0,
            "line_id": 2,
            "line_name": "Portagem - Estacao B",
            "origin_terminal": "Portagem"
        }
    ],
    "status": 200
}
```

### Endpoint 9: Wallet Top-up

- **Description:** Adds funds to the authenticated customer's wallet. Customer access.
- **Method & URL:** `POST http://localhost:8080/dbproj/wallet/topup`
- **Headers:** `Authorization: Bearer <customer_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "amount": 10.0,
    "payment_method": "card"
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "results": {
        "new_balance": 60.0
    },
    "status": 200
}
```

### Endpoint 10: Purchase Ticket

- **Description:** Parses discounts, deducts wallet funds, and issues a ticket. Customer access.
- **Method & URL:** `POST http://localhost:8080/dbproj/purchase`
- **Headers:** `Authorization: Bearer <customer_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "line_id": 2,
    "product_type": "single_trip",
    "travel_date": "2026-05-19"
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "results": {
        "final_price": 1.5,
        "purchase_id": 1006
    },
    "status": 200
}
```

### Endpoint 11: Validate/Use Ticket

- **Description:** Scans an active ticket against a specific station, consuming journey capacity. Customer access.
- **Method & URL:** `POST http://localhost:8080/dbproj/ticket/use/1004`
- **Headers:** `Authorization: Bearer <customer_token>`, `Content-Type: application/json`
- **Request Body (JSON):**

```json
{
    "used_at": "2026-05-19 08:20:00",
    "station_id": 1
}
```

- **Expected Response:**

```json
{
    "errors": null,
    "status": 200
}
```

### Endpoint 12: View Peak/Low Demand

- **Description:** Aggregates line validation capacities by time slots. Admin access.
- **Method & URL:** `GET http://localhost:8080/dbproj/report/demand`
- **Headers:** `Authorization: Bearer <admin_token>`
- **Request Body (JSON):** _None_
- **Expected Response:**

```json
{
    "errors": null,
    "results": [
        {
            "line_id": 1,
            "time_slot": "08:00-08:59",
            "validations": 3
        }
    ],
    "status": 200
}
```

### Endpoint 13: View Top Spenders per Line

- **Description:** Identifies maximum grossing customers per active network line. Admin access.
- **Method & URL:** `GET http://localhost:8080/dbproj/report/top_spenders`
- **Headers:** `Authorization: Bearer <admin_token>`
- **Request Body (JSON):** _None_
- **Expected Response:**

```json
{
    "errors": null,
    "results": [
        {
            "customer_id": 3,
            "line_id": 1,
            "total_spent": 1.5
        }
    ],
    "status": 200
}
```

### Endpoint 14: View Monthly Repeat Customers

- **Description:** Calculates discrete user retention across monthly cohorts. Admin access.
- **Method & URL:** `GET http://localhost:8080/dbproj/report/monthly`
- **Headers:** `Authorization: Bearer <admin_token>`
- **Request Body (JSON):** _None_
- **Expected Response:**

```json
{
    "errors": null,
    "results": [
        {
            "active_customers": 1,
            "line_id": 1,
            "month": 5,
            "repeat_customers": 1
        }
    ],
    "status": 200
}
```

# 3. Testing Concurrency (Safe Behavior)

To demonstrate how the system securely withstands parallel execution load avoiding standard "lost update" phenomenons, we use **Endpoint 9 (`/dbproj/wallet/topup`)** combined with manual Postman Runner parallelism.

### How to Test in Postman:

1. Extract your customer authorization bearer token (via `PUT /dbproj/user`).
2. Add a new `POST` request to `http://localhost:8080/dbproj/wallet/topup` in a Postman Collection.
3. Use this body: `{"amount": 5.00, "payment_method": "multibanco"}`.
4. Open the **Runner** tab in Postman, drag your Collection containing the top-up endpoint inside.
5. Set **Iterations** to `100` and delay to `0` ms.
6. Run the workload.

### Why it remains safe:

In `data_api.py`, immediately inside `wallet_topup()`, the query initiates locking:

```sql
SELECT pessoa_id, wallet FROM cliente WHERE pessoa_id = %s FOR UPDATE
```

By appending `FOR UPDATE`, PostgreSQL physically isolates and locks the customer's wallet row across the entire transaction. If two requests fire in the identical millisecond, Postgres forces the second query cursor to physically run in queue sequence until Request 1 finishes its `UPDATE` and commits. Request 2 then observes the correctly refreshed starting balance preventing race desynchronizations.

# 4. Testing Race Conditions (Mitigation Demonstration)

A critical vulnerability previously existed inside vehicle seating logic within **Endpoint 11 (`/dbproj/ticket/use/`)**, but it has been successfully mitigated.

### Testing the Vehicle Overbooking Protection

1. Identify a valid ticket for a specific voyage (`ticket_id` = 1004). Setup two exact identical POST validations for it.
2. In Postman, leverage the "Send Request" scripts or run the Runner tool concurrently.
3. Validate payload:
    ```json
    {
        "used_at": "2026-05-19 08:20:00",
        "station_id": 1
    }
    ```
4. Query the journey capacity via `GET /dbproj/lines_next`. You will notice that `capacidade_disponivel` correctly stops at `0` and gracefully prevents dropping into negative logic.

### Mitigation Explanation

In `data_api.py`, Endpoint 11 acquires an exclusive row lock on the journey vehicle record object and strictly reads the remaining capacity:

```sql
SELECT v.id, v.capacidade_disponivel FROM viagem v ... LIMIT 1 FOR UPDATE
```

The application now asserts whether the limits are reached and rolls back if exceeded:

```python
if capacidade_disponivel <= 0:
    conn.rollback()
    return flask.jsonify({'status': 400, 'errors': 'A viagem já se encontra na sua lotação máxima.'}), 400
```

Because the Python application enforces this lock check successfully, and the database schema operates with a logical hard limit (`capacidade_disponivel BIGINT CHECK (capacidade_disponivel >= 0)`), the API is fully protected from identical concurrent validations resulting in overbooking constraints.
