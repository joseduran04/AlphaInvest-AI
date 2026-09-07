from __future__ import annotations

import asyncio
from collections import defaultdict
from pathlib import Path
from typing import Any

from generate_api_documentation import (
    HTTP_METHODS,
    PERMISSION_BY_OPERATION,
    PUBLIC_OPERATIONS,
    load_openapi,
)
from sqlalchemy import text

from alphainvest.infrastructure.database.session import AsyncSessionFactory

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIRECTORY = PROJECT_ROOT / "docs"

OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "ENDPOINT_PERMISSION_MATRIX.md"
)

EXPECTED_ROLES = (
    "ADMINISTRADOR",
    "ANALISTA",
    "AUDITOR",
    "INVERSIONISTA",
    "OPERADOR",
)

AUTHENTICATED_ACCESS = "Autenticado"


async def load_role_permissions() -> dict[str, set[str]]:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            text(
                """
                SELECT
                    r.nombre AS rol,
                    p.codigo AS permiso
                FROM app_auth.rol_permisos rp
                JOIN app_auth.roles r
                  ON r.id = rp.rol_id
                JOIN app_auth.permisos p
                  ON p.id = rp.permiso_id
                WHERE r.activo = TRUE
                  AND p.activo = TRUE
                ORDER BY
                    r.nombre,
                    p.codigo
                """
            )
        )

        role_permissions: dict[
            str,
            set[str],
        ] = defaultdict(set)

        for role_name, permission_code in result.all():
            role_permissions[
                str(role_name)
            ].add(
                str(permission_code)
            )

        return dict(role_permissions)


def validate_roles(
    role_permissions: dict[str, set[str]],
) -> None:
    actual_roles = set(
        role_permissions
    )

    expected_roles = set(
        EXPECTED_ROLES
    )

    missing = (
        expected_roles
        - actual_roles
    )

    unexpected = (
        actual_roles
        - expected_roles
    )

    if missing:
        raise RuntimeError(
            "Faltan roles esperados en la base: "
            + ", ".join(
                sorted(missing)
            )
        )

    if unexpected:
        raise RuntimeError(
            "Existen roles no contemplados por "
            "la matriz documental: "
            + ", ".join(
                sorted(unexpected)
            )
        )


def required_permissions(
    method: str,
    path: str,
) -> tuple[str, ...]:
    access = (
        PERMISSION_BY_OPERATION.get(
            (
                method,
                path,
            )
        )
    )

    if (
        access is None
        or access
        == AUTHENTICATED_ACCESS
    ):
        return ()

    return tuple(
        permission.strip()
        for permission in access.split("+")
        if permission.strip()
    )


def access_label(
    method: str,
    path: str,
) -> str:
    key = (
        method,
        path,
    )

    if key in PUBLIC_OPERATIONS:
        return "Público"

    access = (
        PERMISSION_BY_OPERATION.get(
            key
        )
    )

    if access is None:
        return "REVISAR"

    return access


def role_has_access(
    *,
    method: str,
    path: str,
    role_permissions: set[str],
) -> bool:
    key = (
        method,
        path,
    )

    if key in PUBLIC_OPERATIONS:
        return True

    access = (
        PERMISSION_BY_OPERATION.get(
            key
        )
    )

    if access == AUTHENTICATED_ACCESS:
        return True

    permissions = (
        required_permissions(
            method,
            path,
        )
    )

    if not permissions:
        return False

    return all(
        permission in role_permissions
        for permission in permissions
    )


def escape_markdown(
    value: object,
) -> str:
    return (
        str(value)
        .replace("|", "\\|")
        .replace("\n", " ")
    )


def operation_count(
    openapi: dict[str, Any],
) -> int:
    return sum(
        1
        for path_item
        in openapi.get(
            "paths",
            {}
        ).values()
        for method in path_item
        if method in HTTP_METHODS
    )


def validate_operation_security(
    openapi: dict[str, Any],
) -> None:
    missing: list[
        tuple[str, str]
    ] = []

    for path, path_item in openapi.get(
        "paths",
        {},
    ).items():
        for method in path_item:
            if method not in HTTP_METHODS:
                continue

            key = (
                method.upper(),
                path,
            )

            if (
                key
                not in PUBLIC_OPERATIONS
                and key
                not in PERMISSION_BY_OPERATION
            ):
                missing.append(
                    key
                )

    if missing:
        details = "\n".join(
            f"- {method} {path}"
            for method, path in missing
        )

        raise RuntimeError(
            "Existen operaciones sin clasificación "
            "de seguridad:\n"
            f"{details}"
        )


def build_role_summary(
    role_permissions: dict[str, set[str]],
) -> list[str]:
    lines = [
        "## Resumen RBAC",
        "",
        "| Rol | Permisos activos |",
        "|---|---:|",
    ]

    for role in EXPECTED_ROLES:
        lines.append(
            f"| {role} | "
            f"{len(role_permissions[role])} |"
        )

    total_assignments = sum(
        len(permissions)
        for permissions
        in role_permissions.values()
    )

    lines.extend(
        [
            f"| **TOTAL** | **{total_assignments}** |",
            "",
        ]
    )

    return lines


def build_access_summary(
    openapi: dict[str, Any],
    role_permissions: dict[str, set[str]],
) -> list[str]:
    accessible_by_role = {
        role: 0
        for role in EXPECTED_ROLES
    }

    public_count = 0
    authenticated_count = 0
    permission_count = 0

    for path, path_item in openapi[
        "paths"
    ].items():
        for method, operation in path_item.items():
            if method not in HTTP_METHODS:
                continue

            del operation

            http_method = (
                method.upper()
            )

            key = (
                http_method,
                path,
            )

            if key in PUBLIC_OPERATIONS:
                public_count += 1
            else:
                access = (
                    PERMISSION_BY_OPERATION[
                        key
                    ]
                )

                if (
                    access
                    == AUTHENTICATED_ACCESS
                ):
                    authenticated_count += 1
                else:
                    permission_count += 1

            for role in EXPECTED_ROLES:
                if role_has_access(
                    method=http_method,
                    path=path,
                    role_permissions=(
                        role_permissions[
                            role
                        ]
                    ),
                ):
                    accessible_by_role[
                        role
                    ] += 1

    lines = [
        "## Resumen de operaciones",
        "",
        (
            f"- **Operaciones HTTP totales:** "
            f"{operation_count(openapi)}"
        ),
        (
            f"- **Operaciones públicas:** "
            f"{public_count}"
        ),
        (
            f"- **Solo autenticación:** "
            f"{authenticated_count}"
        ),
        (
            f"- **Protegidas por permiso RBAC:** "
            f"{permission_count}"
        ),
        "",
        "### Operaciones accesibles por rol",
        "",
        "| Rol | Operaciones accesibles |",
        "|---|---:|",
    ]

    for role in EXPECTED_ROLES:
        lines.append(
            f"| {role} | "
            f"{accessible_by_role[role]} |"
        )

    lines.append("")

    return lines


def build_endpoint_matrix(
    openapi: dict[str, Any],
    role_permissions: dict[str, set[str]],
) -> list[str]:
    lines = [
        "## Matriz endpoint / permiso / rol",
        "",
        (
            "| Método | Endpoint | Módulo | Acceso | "
            "ADMINISTRADOR | ANALISTA | AUDITOR | "
            "INVERSIONISTA | OPERADOR |"
        ),
        (
            "|---|---|---|---|:---:|:---:|:---:|"
            ":---:|:---:|"
        ),
    ]

    for path, path_item in openapi[
        "paths"
    ].items():
        for method, operation in path_item.items():
            if method not in HTTP_METHODS:
                continue

            http_method = (
                method.upper()
            )

            tags = operation.get(
                "tags",
                [],
            )

            module = (
                ", ".join(tags)
                if tags
                else "-"
            )

            access = access_label(
                http_method,
                path,
            )

            role_cells: list[str] = []

            for role in EXPECTED_ROLES:
                allowed = (
                    role_has_access(
                        method=http_method,
                        path=path,
                        role_permissions=(
                            role_permissions[
                                role
                            ]
                        ),
                    )
                )

                role_cells.append(
                    "✅"
                    if allowed
                    else "—"
                )

            cells = [
                http_method,
                f"`{path}`",
                module,
                (
                    f"`{access}`"
                    if access
                    not in {
                        "Público",
                        AUTHENTICATED_ACCESS,
                    }
                    else access
                ),
                *role_cells,
            ]

            lines.append(
                "| "
                + " | ".join(
                    escape_markdown(
                        cell
                    )
                    for cell in cells
                )
                + " |"
            )

    lines.append("")

    return lines


def build_document(
    openapi: dict[str, Any],
    role_permissions: dict[str, set[str]],
) -> str:
    info = openapi.get(
        "info",
        {},
    )

    lines = [
        "# AlphaInvest AI — Matriz de endpoints y permisos",
        "",
        (
            "Documento generado a partir del OpenAPI real "
            "del backend y de las asignaciones RBAC activas "
            "almacenadas en PostgreSQL/Supabase."
        ),
        "",
        "## Información general",
        "",
        (
            f"- **API:** "
            f"{info.get('title', '-')}"
        ),
        (
            f"- **Versión:** "
            f"{info.get('version', '-')}"
        ),
        "- **Base path:** `/api/v1`",
        "- **Autenticación:** HTTP Bearer",
        "",
        "## Convenciones",
        "",
        (
            "- `Público`: el endpoint no exige "
            "access token."
        ),
        (
            "- `Autenticado`: exige una sesión "
            "Bearer válida, sin permiso granular adicional."
        ),
        (
            "- Un código como `activos.leer` representa "
            "un permiso RBAC obligatorio."
        ),
        (
            "- Los permisos separados por `+` deben "
            "cumplirse simultáneamente."
        ),
        (
            "- `✅`: el rol posee todos los permisos "
            "necesarios para la operación."
        ),
        (
            "- `—`: el rol no posee todos los permisos "
            "necesarios."
        ),
        (
            "- La matriz refleja permisos RBAC; las reglas "
            "de propiedad del recurso continúan aplicando."
        ),
        "",
    ]

    lines.extend(
        build_role_summary(
            role_permissions
        )
    )

    lines.extend(
        build_access_summary(
            openapi,
            role_permissions,
        )
    )

    lines.extend(
        build_endpoint_matrix(
            openapi,
            role_permissions,
        )
    )

    lines.extend(
        [
            "## Fuente de verdad",
            "",
            (
                "- Endpoints y métodos: "
                "`openapi_alphainvest.json`."
            ),
            (
                "- Clasificación endpoint/permiso: "
                "`scripts/generate_api_documentation.py`."
            ),
            (
                "- Asignaciones rol/permiso: "
                "`app_auth.roles`, `app_auth.permisos` y "
                "`app_auth.rol_permisos`."
            ),
            "",
            (
                "La matriz debe regenerarse cuando cambien "
                "endpoints, permisos o asignaciones de roles."
            ),
            "",
        ]
    )

    return "\n".join(
        lines
    )


async def main() -> None:
    openapi = load_openapi()

    validate_operation_security(
        openapi
    )

    role_permissions = (
        await load_role_permissions()
    )

    validate_roles(
        role_permissions
    )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = build_document(
        openapi,
        role_permissions,
    )

    OUTPUT_PATH.write_text(
        document,
        encoding="utf-8",
    )

    total_assignments = sum(
        len(permissions)
        for permissions
        in role_permissions.values()
    )

    print(
        "Matriz endpoint/permisos generada "
        "correctamente."
    )
    print(
        f"Operaciones documentadas: "
        f"{operation_count(openapi)}"
    )
    print(
        f"Roles documentados: "
        f"{len(role_permissions)}"
    )
    print(
        f"Asignaciones RBAC: "
        f"{total_assignments}"
    )

    for role in EXPECTED_ROLES:
        print(
            f"{role}: "
            f"{len(role_permissions[role])} "
            "permisos"
        )

    print(
        f"Archivo: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )