# VOID

**DDD + Hexagonal Architecture FastAPI Boilerplate**

A production-ready boilerplate for building FastAPI applications with Domain-Driven Design and Hexagonal Architecture patterns.

## Features

- **Domain-Driven Design**: Clean separation of domain logic from infrastructure
- **Hexagonal Architecture**: Port-Adapter pattern for flexible dependency management
- **FastAPI**: Modern, fast web framework with automatic OpenAPI documentation
- **MongoDB**: Async database operations with Motor
- **AWS SQS**: FIFO queue integration for async task processing
- **Unit of Work**: Transaction support with MongoDB replica sets
- **Three Entrypoints**: API, Worker, CLI for different use cases

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url> your-project
cd your-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r src/requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
vi .env
```

### 3. Run the Application

```bash
# API Server (development)
./void run api

# SQS Worker
./void run worker

# CLI Job
./void run job <JOB_NAME>
```

## Project Structure

```
src/
├── domain/              # Pure Python domain logic
│   ├── entities/        # Domain entities
│   ├── ports/           # Abstract interfaces
│   └── value_objects/   # Enums and value objects
├── service_layer/       # Application services
│   ├── application/     # Use case implementations
│   └── exceptions.py    # Business exceptions
├── adapters/            # Infrastructure implementations
│   ├── aws/             # SQS client/producer/consumer
│   ├── http/            # HTTP client (httpx)
│   ├── mongodb/         # MongoDB adapters
│   ├── repositories/    # Repository implementations
│   └── uow/             # Unit of Work
├── entrypoints/         # Application entry points
│   ├── api/             # FastAPI application
│   ├── worker/          # SQS Worker
│   └── cli/             # CLI Jobs
└── config.py            # Configuration
```

## Available Commands

```bash
# Start API server with hot reload
./void run api

# Start SQS consumer worker
./void run worker

# Run a specific CLI job
./void run job process_item --item-id 507f1f77bcf86cd799439011

# List available jobs
./void run job list
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/api/v1/items` | Create item |
| GET | `/api/v1/items/{id}` | Get item by ID |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `development` |
| `DEBUG` | Debug mode | `true` |
| `MONGODB_URI` | MongoDB connection URI | `mongodb://localhost:27017` |
| `MONGODB_NAME` | Database name | `void` |
| `AWS_ACCESS_KEY_ID` | AWS access key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - |
| `AWS_REGION` | AWS region | `ap-northeast-2` |
| `SQS_QUEUE_URL` | SQS FIFO queue URL | - |

## Architecture

This project follows **Domain-Driven Design (DDD)** and **Hexagonal Architecture** principles:

### Layers

1. **Domain Layer** (`domain/`)
   - Pure Python with no external dependencies
   - Contains entities, value objects, and port interfaces

2. **Service Layer** (`service_layer/`)
   - Application services implementing use cases
   - Orchestrates domain logic and infrastructure

3. **Adapters Layer** (`adapters/`)
   - Infrastructure implementations
   - MongoDB repositories, AWS clients, HTTP clients

4. **Entrypoints Layer** (`entrypoints/`)
   - Application entry points
   - API routes, Worker tasks, CLI jobs

### Key Patterns

- **Repository Pattern**: Abstract data access through interfaces
- **Unit of Work**: Transactional consistency (use only for multi-write operations)
- **Dependency Injection**: FastAPI's Depends for loose coupling
- **Task Registry**: Decorator-based worker task registration
- **Job Registry**: Decorator-based CLI job registration
- **Exception Pattern**: Class-level `status_code`/`error_type` for automatic HTTP response mapping

## Development

### Adding a New Entity

1. Create entity in `domain/entities/` (with `create()` factory method)
2. Define repository port in `domain/ports/`
3. Add value objects in `domain/value_objects/` (if needed)
4. Implement MongoDB adapter in `adapters/mongodb/collections/`
5. Implement repository in `adapters/repositories/mongodb/`
6. Register repository in `adapters/uow/mongo_unit_of_work.py`

### Adding a New API Endpoint

1. Create schemas in `entrypoints/api/schemas/`
2. Create route handler in `entrypoints/api/routes/`
3. Register router in `entrypoints/api/routes/__init__.py`

### Adding a New Worker Task

1. Create task handler with `@task` decorator in `entrypoints/worker/tasks/`
2. Add module to `TASK_MODULES` in `entrypoints/worker/tasks/__init__.py`

### Adding a New CLI Job

1. Create job handler with `@job` decorator in `entrypoints/cli/jobs/`
2. Add module to `JOB_MODULES` in `entrypoints/cli/jobs/__init__.py`

### Adding a New Exception

1. Define exception in `service_layer/exceptions.py` inheriting from `ServiceError`
2. Set `status_code` and `error_type` class attributes
3. Exception is automatically handled by API (no additional registration needed)

## Requirements

- Python 3.9+
- MongoDB (Replica Set for transactions)
- AWS Account (for SQS)

## License

MIT License
