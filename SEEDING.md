# Database Seeding Guide

## Quick Start

### Option 1: Automatic Smart Seeding with Docker Compose (Recommended)
```bash
# This will automatically run migrations + smart seeding + start the server
docker-compose up
```

**Smart Behavior**: Only seeds when database is empty, skips if data already exists.

### Option 2: Manual Seeding
```bash
# Manual seeding (only seeds if database is empty)
docker-compose run --rm app python manage.py seed_all

# Force re-seeding (overwrites existing data)
docker-compose run --rm app python manage.py seed_all --force
```

Both options will:
1. ✅ Check if required tables exist
2. ✅ Run migrations if needed
3. ✅ **Smart Check**: Only seed if database is empty
4. ✅ Seed courier data (DHL, shipment types, routes)
5. ✅ Seed courier configurations (API keys, settings)
6. ✅ Start the development server (Option 1 only)

## Available Commands

### `seed_all` - Complete Seeding
```bash
# Full seeding (migrations + data)
docker-compose run --rm app python manage.py seed_all

# Skip migrations (assumes they're already run)
docker-compose run --rm app python manage.py seed_all --skip-migrations

# Force re-seeding (useful for development)
docker-compose run --rm app python manage.py seed_all --force
```

### Individual Seeding Commands
```bash
# Seed only courier data
docker-compose run --rm app python manage.py seed_courier_data

# Seed only courier configurations
docker-compose run --rm app python manage.py seed_courier_config
```

## What Gets Seeded

### Courier Data (`seed_courier_data`)
- **DHL Courier**: Basic courier information
- **Shipment Types**: NORMAL, URGENT, SAME_DAY_DELIVERY
- **Routes**: Bonn ↔ Berlin
- **Courier-Shipment Type Links**: DHL supports all shipment types
- **Courier-Route Links**: DHL supports all routes

### Courier Config (`seed_courier_config`)
- **DHL Configuration**: API keys, base URLs, credentials
- **FedEx Configuration**: Placeholder config
- **UPS Configuration**: Placeholder config

## Development Workflow

### Fresh Start (Delete & Recreate Everything)
1. **Delete Database**: `docker-compose down -v` (removes volumes)
2. **Start with Auto-Seeding**: `docker-compose up` (migrations + smart seeding + server)

### Quick Restart (Keep Data)
1. **Restart**: `docker-compose restart` (keeps existing data, skips seeding)
2. **Or Stop/Start**: `docker-compose down && docker-compose up` (keeps existing data, skips seeding)

### Force Re-Seeding (Development)
1. **Force Seed**: `docker-compose run --rm app python manage.py seed_all --force`
2. **Start App**: `docker-compose up`

### Manual Seeding Only
1. **Seed Data**: `docker-compose run --rm app python manage.py seed_all` (only if empty)
2. **Start App**: `docker-compose up`

## API Endpoints

After seeding, your API endpoints will be available at:

- **Create Shipment**: `POST /api/v1/shipment-requests/`
- **Get Label**: `GET /api/v1/shipment-labels/{reference_number}/`
- **Track Shipment**: `GET /api/v1/shipments/{reference_number}/track/`

## Troubleshooting

- **Tables don't exist**: The command will automatically run migrations
- **Data already exists**: Use `--force` flag to re-seed
- **API not working**: Check that containers are running with `docker-compose ps`
- **Migration errors**: Check your migration files and database connection
