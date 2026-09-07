from collections.abc import MutableMapping
from logging.config import fileConfig
from typing import Any, Literal

from alembic import context
from sqlalchemy import engine_from_config, pool

from alphainvest.core.config import get_settings
from alphainvest.infrastructure.database.base import Base
from alphainvest.modules.ai.infrastructure import models as ai_models  # noqa: F401
from alphainvest.modules.audit.infrastructure import models as audit_models  # noqa: F401
from alphainvest.modules.auth.infrastructure import models as auth_models  # noqa: F401
from alphainvest.modules.market.infrastructure import models as market_models  # noqa: F401
from alphainvest.modules.operation.infrastructure import models as operation_models  # noqa: F401
from alphainvest.modules.portfolio.infrastructure import models as portfolio_models  # noqa: F401
from alphainvest.modules.profile.infrastructure import models as profile_models  # noqa: F401
from alphainvest.modules.simulation.infrastructure import models as simulation_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()

config.set_main_option(
    "sqlalchemy.url",
    settings.alembic_database_url,
)

target_metadata = Base.metadata

MANAGED_SCHEMAS = {
    "ai",
    "audit",
    "app_auth",
    "market",
    "operation",
    "portfolio",
    "profile",
    "simulation",
}

SQL_MANAGED_TABLES = {
    "audit.errores_aplicacion",
    "audit.registros_auditoria",
    "operation.control_procesos",
    "operation.registros_respaldo",
    "operation.versiones_esquema",
    "operation.alembic_version",
}


def include_name(
    name: str | None,
    type_: Literal[
        "schema",
        "table",
        "column",
        "index",
        "unique_constraint",
        "foreign_key_constraint",
    ],
    parent_names: MutableMapping[
        Literal[
            "schema_name",
            "table_name",
            "schema_qualified_table_name",
        ],
        str | None,
    ],
) -> bool:
    """Limita la reflexión de Alembic a los esquemas administrados."""

    if type_ == "schema":
        return name in MANAGED_SCHEMAS

    return True


def include_object(
    object_: Any,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """Protege objetos SQL que no pertenecen al metadata ORM."""

    if type_ != "table":
        return True

    schema = getattr(object_, "schema", None)

    if schema is None and compare_to is not None:
        schema = getattr(compare_to, "schema", None)

    qualified_name = f"{schema}.{name}"

    if qualified_name in SQL_MANAGED_TABLES:
        return False

    # Seguridad adicional:
    # nunca generar DROP TABLE para una tabla existente que no esté
    # representada en Base.metadata.
    if reflected and compare_to is None:
        return False

    return True


def run_migrations_offline() -> None:
    context.configure(
        url=settings.alembic_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_schemas=True,
        include_name=include_name,
        include_object=include_object,
        version_table_schema="operation",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,
            include_name=include_name,
            include_object=include_object,
            version_table_schema="operation",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
