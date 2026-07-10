-- Run this once while connected as a PostgreSQL administrator.
-- It lets Django create and destroy its isolated test database.
ALTER ROLE petkit_admin CREATEDB;
