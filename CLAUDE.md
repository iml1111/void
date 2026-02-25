# VOID Project Context

**DDD + Hexagonal Architecture FastAPI Boilerplate**

---

## Project Overview

VOID is a FastAPI boilerplate following DDD + Hexagonal Architecture patterns.
It is designed to be cloned and used as a starting point for real service development.

**Tech Stack**: Python 3.9+ | FastAPI | MongoDB (Motor) | AWS SQS (FIFO) | httpx

---

## Architecture Principles

### 1. Domain-Driven Design (DDD)
- **Domain Layer**: Pure Python, no external dependencies
- **Service Layer**: Use Case implementation, orchestrates Domain and Infrastructure
- **Infrastructure Layer**: External system integration (DB, API)

### 2. Hexagonal Pattern
- **Port**: Interface (abstraction) - `domain/ports/`
- **Adapter**: Implementation (tech stack) - `adapters/`
- Domain depends on Port, Adapter is independent of Domain

### 3. Identity-Based Equality
Entities are identified by ID (`__eq__`, `__hash__`), usable as Set/Dict keys

---

## Directory Structure

```
src/
├── domain/              # Pure Python (no external dependencies)
│   ├── entities/        # Domain entities with identity-based equality
│   ├── ports/           # Abstract interfaces (repositories)
│   └── value_objects/   # Enums and value objects
├── services/            # Use Cases
│   ├── application/     # Application services
│   └── exceptions.py    # Service layer exceptions (with status_code/error_type)
├── adapters/            # Infrastructure implementations
│   ├── aws/             # SQS client, producer, consumer
│   ├── http/            # HTTP client (httpx)
│   ├── mongodb/         # MongoDB client, collections, base adapter
│   ├── repositories/    # Repository implementations
│   └── uow/             # Unit of Work implementation
├── entrypoints/         # Application entry points
│   ├── api/             # FastAPI (routes, schemas, dependencies)
│   ├── worker/          # SQS Worker (tasks, task_registry)
│   └── cli/             # CLI Jobs (jobs, job_registry)
├── config.py            # Pydantic BaseSettings
└── __about__.py         # Version info
```

---

## Key Design Patterns

### 1. Async/Await Pattern
**Consistent async/await usage across the entire project**

```python
# Repository Layer
async def create(self, entity: ItemEntity) -> str:
    doc = BaseMongoAdapter.prepare_for_insert(entity.to_dict())
    result = await self._adapter.insert_one(doc)
    return str(result.inserted_id)

# Service Layer (single read: direct repository call)
async def get_item(self, item_id: str) -> ItemEntity:
    item = await self._item_repo.get_by_id(item_id)
    if not item:
        raise ItemNotFoundError(f"Item {item_id} not found")
    return item
```

---

### 2. BaseEntity Pattern
**Requirements**: `@dataclass(eq=False, frozen=True)`, `from_dict()`, `validate()`, Identity-based equality

```python
@dataclass(eq=False, frozen=True)
class ItemEntity(BaseEntity):
    name: str
    description: str
    status: ItemStatus
    created_at: datetime
    id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def create(cls, name: str, ...) -> "ItemEntity":
        """Factory method for new entity creation"""
        return cls(name=name, created_at=datetime.now(timezone.utc), ...)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemEntity":
        # _id → id conversion, field filtering
        ...

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("Item name is required")

    def __eq__(self, other): return self.id == other.id
    def __hash__(self): return hash(self.id)
```

---

### 3. Repository Pattern
**Structure**: ABC Interface (Port) → MongoDB Implementation (Adapter)

```python
# Port (domain/ports/item.py)
class ItemRepository(ABC):
    @abstractmethod
    async def create(self, entity: ItemEntity) -> str: ...

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[ItemEntity]: ...

# Adapter (adapters/repositories/mongodb/item.py)
class MongoItemRepository(ItemRepository):
    async def create(self, entity: ItemEntity) -> str:
        doc = BaseMongoAdapter.prepare_for_insert(entity.to_dict())
        result = await self._adapter.insert_one(doc)
        return str(result.inserted_id)
```

---

### 4. Unit of Work (UoW) Pattern
**Purpose**: Guarantee atomicity of multiple write operations

**Principles**:
- Use only when 2+ writes require atomic processing
- Single read/write should call the repository directly

```python
# Multiple writes: UoW
async with MongoUnitOfWork(db_client) as uow:
    await uow.item_repo.create(entity1)
    await uow.item_repo.create(entity2)
    await uow.commit()

# Single read: direct call
item = await self._item_repo.get_by_id(item_id)
```

**Requirement**: MongoDB Replica Set (transaction support)

---

### 5. Exception Pattern
**Domain exceptions are pure Python, converted to HTTPException at each API Route**

```python
# domain/exceptions.py - Pure Python (no HTTP concepts)
class DomainError(Exception):
    """Base exception for all domain errors"""
    pass

class EntityNotFoundError(DomainError):
    """Entity with given ID does not exist"""
    pass

class ItemNotFoundError(EntityNotFoundError):
    """Item with given ID does not exist"""
    pass

class ItemValidationError(DomainError):
    """Item data validation failed"""
    pass

# API Route - try-except + HTTPException conversion
@router.get("/{item_id}")
async def get_item(item_id: str, service = Depends(get_item_service)):
    try:
        item = await service.get_item(item_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ItemResponse(...)

# 5XX errors are automatically handled by @app.exception_handler(Exception)
```

---

### 6. Lifespan Singleton Pattern
**Purpose**: Initialize heavy resources (e.g., DB connection pool) once at app startup

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize singletons
    app.state.db_client = MongoDBClient(uri=config.mongodb_uri, ...)
    yield
    # Shutdown: Cleanup
    app.state.db_client.close()
```

---

### 7. Task/Job Registry Pattern (Auto-Discovery)
**One-step registration**: Just attach the decorator for automatic registration (no `__init__.py` modification needed when adding new files to the package)

**Worker**: `@task` decorator immediately registers SQS message handlers
**CLI**: `@job` decorator immediately registers cronjob/background jobs (auto-generates Click options based on function signature)

```python
# Worker task - @task immediately registers to TaskRegistry
@task
async def process_item(data: Dict[str, Any]) -> None:
    service = ItemService(db_client)
    await service.create_item(name=data["name"], ...)

# CLI job - @job immediately registers to JobRegistry
@job
async def process_item(item_id: str) -> None:
    """Process item by ID"""  # docstring is displayed in --help
    service = ItemService(db_client)
    item = await service.get_item(item_id)
# Run: ./void run job process-item --item-id xxx
```

**How Auto-Discovery works**:
- `discover_tasks()` / `discover_jobs()` recursively import all `.py` files within the package
- `@task` / `@job` decorators execute and immediately register to the Registry
- New files are automatically recognized without modifying `__init__.py`

---

## Entrypoints

### API (FastAPI)
```bash
./void run api  # uvicorn with --reload
```

**Structure**: `app.py` → `lifespan` → `middleware` → `exception_handlers` → `routes`

### Worker (SQS Consumer)
```bash
./void run worker
```

**Structure**: `app.py` → `dependencies.initialize()` → `discover_tasks()` → `consumer.start()`

### CLI (Click)
```bash
./void run job                    # Show help
./void run job list               # List registered jobs
./void run job process-item --help                              # Job help
./void run job process-item --item-id 507f1f77bcf86cd799439011  # Run job
```

**Structure**: `app.py` → `discover_jobs()` → `create_all_job_commands()` → Dynamic Click Command generation
**Features**:
- `@job` decorator analyzes function signature to auto-generate Click options
- snake_case function name → kebab-case command name conversion
- Function docstring is displayed in `--help`
- No `__init__.py` modification needed when adding new files

---

## Current API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/items` | Create item |
| GET | `/api/v1/items/{id}` | Get item by ID |

---

## Configuration

Environment variables are set via `.env` file or system environment variables:

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_NAME=void

# AWS
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=ap-northeast-2
SQS_QUEUE_URL=https://sqs.ap-northeast-2.amazonaws.com/xxx/queue.fifo
```

---

## Adding New Features

### New Entity
1. `domain/entities/xxx.py` - Define entity (include `create()` factory method)
2. `domain/ports/xxx.py` - Define repository ABC
3. `domain/value_objects/xxx_enums.py` - Define enums (if needed)
4. `adapters/mongodb/collections/xxx_adapter.py` - Collection adapter
5. `adapters/repositories/mongodb/xxx.py` - Repository implementation
6. `adapters/uow/mongo_unit_of_work.py` - Add repository to UoW

### New API Endpoint
1. `entrypoints/api/schemas/xxx.py` - Request/Response schemas
2. `entrypoints/api/routes/xxx.py` - Route handlers
3. `entrypoints/api/routes/__init__.py` - Register router
4. `entrypoints/api/dependencies/services.py` - Add service dependency

### New Worker Task
1. `entrypoints/worker/tasks/xxx.py` - Define handler with @task decorator
   - No `__init__.py` modification needed (Auto-discovery)

### New CLI Job
1. `entrypoints/cli/jobs/xxx.py` - Define handler with @job decorator
   - No `__init__.py` modification needed (Auto-discovery)

### New Exception
1. `domain/exceptions.py` - Inherit from `DomainError` or appropriate base exception
2. `domain/__init__.py` - Add exception export
3. Convert to `HTTPException` via `try-except` in API Route
