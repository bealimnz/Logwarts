from logwarts.models.log_event import LogEvent
from logwarts.models.context import LogContext
from logwarts.models.exception import LogException


log = LogEvent(
    level="ERROR",
    logger_name="user_service",
    message="Error ao criar usuário",
    context=LogContext(
        service="auth-api",
        environment="dev",
        host="localhost",
        correlation_id="abc-123"
    ),
    exception=LogException(
        type="ValueError",
        message="email inválido"
    )
)

print(log.model_dump_json())

