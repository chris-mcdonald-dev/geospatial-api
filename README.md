# Running the Project

## Prerequisites

- Docker Compose (If you don't have a DB already running)
- Update the values in the `.env.sample` file and rename to `.env`
- Run `pip install -r requirements.txt` in your virtual environment

## How to Run

#### Creating & Running the DB

1. Create & start the DB using Docker Compose (skip if you already have a DB running):
   ```bash
   docker compose up
   ```
   - The DB will be available at `http://localhost:5432`.

#### Running DB Migrations (And seeding with provided parquet files)

2. Defines the DB table schemas, and seeds the DB with alembic:

   - This takes some time (1.2 mil rows). Takes about 30-50 secondes on my computer (did my best to optimize this)

   - ```bash
      alembic upgrade head
     ```

3. Run the backend server:

   - ```bash
     fastapi dev
     ```
