# VOID Project Context

**DDD + Hexagonal Architecture FastAPI Boilerplate**

---

## Project Overview

VOID는 DDD + Hexagonal Architecture 패턴을 따르는 FastAPI 보일러플레이트입니다.
실제 서비스 개발 시 clone하여 사용할 수 있도록 설계되었습니다.

**기술 스택**: Python 3.9+ | FastAPI | MongoDB (Motor) | AWS SQS (FIFO) | httpx

---

## Architecture Principles

### 1. Domain-Driven Design (DDD)
- **Domain Layer**: 순수 Python, 외부 의존성 없음
- **Service Layer**: Use Case 구현, Domain-Infrastructure 조율
- **Infrastructure Layer**: 외부 시스템 통합 (DB, API)

### 2. Hexagonal Pattern
- **Port**: Interface (추상화) - `domain/ports/`
- **Adapter**: 구현체 (기술 스택) - `adapters/`
- Domain → Port 의존, Adapter는 Domain 독립

### 3. Identity-Based Equality
Entity는 ID로 식별 (`__eq__`, `__hash__`), Set/Dict 키로 사용 가능

---

## Directory Structure

```
src/
├── domain/              # Pure Python (no external dependencies)
│   ├── entities/        # Domain entities with identity-based equality
│   ├── ports/           # Abstract interfaces (repositories)
│   └── value_objects/   # Enums and value objects
├── service_layer/       # Use Cases
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
**전체 프로젝트에서 async/await 일관 사용**

```python
# Repository Layer
async def create(self, entity: ItemEntity) -> str:
    doc = BaseMongoAdapter.prepare_for_insert(entity.to_dict())
    result = await self._adapter.insert_one(doc)
    return str(result.inserted_id)

# Service Layer (단일 read: 직접 repository 호출)
async def get_item(self, item_id: str) -> ItemEntity:
    item = await self._item_repo.get_by_id(item_id)
    if not item:
        raise ItemNotFoundError(f"Item {item_id} not found")
    return item
```

---

### 2. BaseEntity Pattern
**요구사항**: `@dataclass(eq=False, frozen=True)`, `from_dict()`, `validate()`, Identity-based equality

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
**구조**: ABC Interface (Port) → MongoDB Implementation (Adapter)

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
**목적**: 다중 write 작업의 원자성 보장

**원칙**:
- ✅ 2+ write가 원자적 처리 필요 시만 사용
- ❌ 단일 read/write는 직접 repository 호출

```python
# 다중 write: UoW
async with MongoUnitOfWork(db_client) as uow:
    await uow.item_repo.create(entity1)
    await uow.item_repo.create(entity2)
    await uow.commit()

# 단일 read: 직접 호출
item = await self._item_repo.get_by_id(item_id)
```

**요구사항**: MongoDB Replica Set (트랜잭션 지원)

---

### 5. Exception Pattern
**Domain 예외는 순수 Python, 각 API Route에서 HTTPException으로 변환**

```python
# domain/exceptions.py - 순수 Python (HTTP 개념 없음)
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

# API Route - try-except + HTTPException 변환
@router.get("/{item_id}")
async def get_item(item_id: str, service = Depends(get_item_service)):
    try:
        item = await service.get_item(item_id)
    except ItemNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ItemResponse(...)

# 5XX 에러는 @app.exception_handler(Exception)이 자동 처리
```

---

### 6. Lifespan Singleton Pattern
**목적**: 무거운 리소스(DB 커넥션 풀)를 앱 시작 시 1회 초기화

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

### 7. Task/Job Registry Pattern
**Worker**: `@task` 데코레이터로 SQS 메시지 핸들러 등록
**CLI**: `@job` 데코레이터로 cronjob/background job 등록

```python
# Worker task (Write 예시)
@task
async def process_item(data: Dict[str, Any]) -> None:
    service = ItemService(db_client)
    await service.create_item(name=data["name"], ...)

# CLI job (Read 예시)
@job
async def process_item(item_id: str) -> None:
    service = ItemService(db_client)
    item = await service.get_item(item_id)
```

---

## Entrypoints

### API (FastAPI)
```bash
./void run api  # uvicorn with --reload
```

**구조**: `app.py` → `lifespan` → `middleware` → `exception_handlers` → `routes`

### Worker (SQS Consumer)
```bash
./void run worker
```

**구조**: `app.py` → `dependencies.initialize()` → `register_all_tasks()` → `consumer.start()`

### CLI (Click)
```bash
./void run job <JOB_NAME>
./void run job process_item --item-id 507f1f77bcf86cd799439011
```

**구조**: `app.py` → `dependencies.initialize()` → `register_all_jobs()` → `handler.execute()`

---

## Current API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/items` | Create item |
| GET | `/api/v1/items/{id}` | Get item by ID |

---

## Configuration

환경변수는 `.env` 파일 또는 시스템 환경변수로 설정:

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
1. `domain/entities/xxx.py` - Entity 정의 (`create()` factory method 포함)
2. `domain/ports/xxx.py` - Repository ABC 정의
3. `domain/value_objects/xxx_enums.py` - Enum 정의 (필요시)
4. `adapters/mongodb/collections/xxx_adapter.py` - Collection adapter
5. `adapters/repositories/mongodb/xxx.py` - Repository 구현
6. `adapters/uow/mongo_unit_of_work.py` - UoW에 repository 추가

### New API Endpoint
1. `entrypoints/api/schemas/xxx.py` - Request/Response schemas
2. `entrypoints/api/routes/xxx.py` - Route handlers
3. `entrypoints/api/routes/__init__.py` - Router 등록
4. `entrypoints/api/dependencies/services.py` - Service dependency 추가

### New Worker Task
1. `entrypoints/worker/tasks/xxx.py` - @task 데코레이터로 핸들러 정의
2. `entrypoints/worker/tasks/__init__.py` - TASK_MODULES에 추가

### New CLI Job
1. `entrypoints/cli/jobs/xxx.py` - @job 데코레이터로 핸들러 정의
2. `entrypoints/cli/jobs/__init__.py` - JOB_MODULES에 추가

### New Exception
1. `domain/exceptions.py` - `DomainError` 또는 적절한 기본 예외 상속
2. `domain/__init__.py` - 예외 export 추가
3. API Route에서 `try-except` + `HTTPException` 변환
