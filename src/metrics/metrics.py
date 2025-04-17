from prometheus_client import Counter, Gauge, Histogram, generate_latest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, text
from fastapi import Request
from fastapi.responses import PlainTextResponse
import time
from datetime import datetime, timedelta
from models.models import User, Document, Patient, Role

REQUEST_COUNT = Counter(
    'http_requests_total',
    'Сумма всех HTTP Запросов',
    ['method', 'endpoint', 'status_code']
)

DAU = Gauge('dau', 'Daily Active Users')
DOCUMENTS_TOTAL = Gauge('documents_total', 'Total uploaded documents')
DOCUMENTS_BY_TYPE = Counter(
    'documents_by_type',
    'Documents count by category',
    ['document_type']
)

DB_ACTIVE_CONNECTIONS = Gauge(
    'db_active_connections',
    'Количество активных подключений к Базе Данных'
)

DB_RESPONSE_TIME = Histogram(
    'db_query_duration_seconds',
    'Database response time distribution',
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.5, 1]
)

APP_HEALTH = Gauge(
    'app_health',
    'Health status of the application (1 = healthy, 0 = unhealthy)'
)

HTTP_ERRORS = Counter(
    'http_errors_total',
    'HTTP errors (4xx and 5xx)',
    ['method', 'endpoint', 'status_code']
)

AVG_PATIENT_AGE = Gauge(
    "patient_avg_age",
    "Average patient age"
)

USERS_BY_ROLE = Gauge(
    'users_by_role',
    'Users count by role',
    ['role_name']
)

PATIENTS_AGE_DISTRIBUTION = Histogram(
    'patients_age_distribution',
    'Patients age distribution',
    buckets=[0, 3, 6, 9, 12, 15, 18]
)

NEW_PATIENTS_TOTAL = Counter(
    'new_patients_registered_total',
    'Новый пациенты в системе'
)

API_RESPONSE_TIME = Histogram(
    'api_response_time_seconds',
    'API response time distribution',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
)

async def update_metrics(session: AsyncSession):
    try:
        start_time = time.time()
        await session.execute(text("SELECT 1"))
        duration = time.time() - start_time
        DB_RESPONSE_TIME.observe(duration)

        connections = await session.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
        )
        DB_ACTIVE_CONNECTIONS.set(connections.scalar())

        active_users = await session.execute(
            select(func.count(User.id)).where(User.active == True)
        )
        dau = active_users.scalar()
        APP_HEALTH.set(1 if dau is not None else 0)

    except Exception as e:
        APP_HEALTH.set(0)
        DB_RESPONSE_TIME.observe(5)
        raise e

    active_users = await session.execute(
        select(func.count(User.id)).where(User.active == True)
    )
    DAU.set(active_users.scalar())

    new_patients_last_hour = await session.execute(
        select(func.count(Patient.id))
        .where(Patient.created_at >= datetime.now() - timedelta(hours=1))
    )
    NEW_PATIENTS_TOTAL.inc(new_patients_last_hour.scalar())

    patients = await session.execute(select(Patient))
    for patient in patients.scalars():
        PATIENTS_AGE_DISTRIBUTION.observe(patient.age)

    roles_count = await session.execute(
        select(Role.name, func.count(User.id))
        .join(User)
        .group_by(Role.name)
    )
    for role_name, count in roles_count:
        USERS_BY_ROLE.labels(role_name=role_name).set(count)

    avg_age_result = await session.execute(select(func.avg(Patient.age)))
    avg_age = avg_age_result.scalar()
    AVG_PATIENT_AGE.set(avg_age if avg_age is not None else 0)

    total_docs = await session.execute(select(func.count(Document.id)))
    DOCUMENTS_TOTAL.set(total_docs.scalar())

    docs_by_type = await session.execute(
        select(Document.subdirectory_type, func.count(Document.id))
        .group_by(Document.subdirectory_type)
    )
    for doc_type, count in docs_by_type:
        DOCUMENTS_BY_TYPE.labels(document_type=doc_type.value).inc(count)

def get_metrics(request: Request):
    return PlainTextResponse(
        generate_latest(),
        media_type='text/plain'
    )