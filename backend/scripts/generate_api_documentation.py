from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OPENAPI_PATH = PROJECT_ROOT / "openapi_alphainvest.json"

OUTPUT_DIRECTORY = PROJECT_ROOT / "docs"

OUTPUT_PATH = (
    OUTPUT_DIRECTORY
    / "API_REFERENCE.md"
)

HTTP_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
}

PERMISSION_BY_OPERATION: dict[
    tuple[str, str],
    str,
] = {
    (
        "GET",
        "/api/v1/profile/current",
    ): "Autenticado",
    (
        "GET",
        "/api/v1/profile/history",
    ): "Autenticado",
    (
        "POST",
        "/api/v1/profile/evaluations",
    ): "Autenticado",
    (
        "GET",
        "/api/v1/auth/me",
    ): "Autenticado",

    (
        "GET",
        "/api/v1/market/markets",
    ): "activos.leer",
    (
        "GET",
        "/api/v1/market/asset-types",
    ): "activos.leer",
    (
        "GET",
        "/api/v1/market/sources",
    ): "fuentes.leer",
    (
        "GET",
        "/api/v1/market/assets",
    ): "activos.leer",
    (
        "GET",
        "/api/v1/market/assets/{asset_id}",
    ): "activos.leer",
    (
        "GET",
        "/api/v1/market/assets/{asset_id}/prices",
    ): "precios.leer",
    (
        "GET",
        "/api/v1/market/assets/{asset_id}/latest-price",
    ): "precios.leer",
    (
        "POST",
        "/api/v1/market/assets/{asset_id}/prices/sync",
    ): "precios.cargar",
    (
        "POST",
        "/api/v1/market/assets/{asset_id}/indicators/calculate",
    ): "indicadores.calcular",
    (
        "GET",
        "/api/v1/market/assets/{asset_id}/indicators",
    ): "indicadores.leer",
    (
        "GET",
        "/api/v1/market/synchronizations",
    ): "trabajos.leer",
    (
        "GET",
        "/api/v1/market/synchronizations/{execution_id}",
    ): "trabajos.leer",

    (
        "POST",
        "/api/v1/portfolios",
    ): "portafolios.crear",
    (
        "GET",
        "/api/v1/portfolios",
    ): "portafolios.leer",
    (
        "GET",
        "/api/v1/portfolios/{portfolio_id}",
    ): "portafolios.leer",
    (
        "PATCH",
        "/api/v1/portfolios/{portfolio_id}",
    ): "portafolios.actualizar",
    (
        "GET",
        "/api/v1/portfolios/{portfolio_id}/summary",
    ): "portafolios.leer",
    (
        "GET",
        "/api/v1/portfolios/{portfolio_id}/allocation/assets",
    ): "portafolios.leer",
    (
        "GET",
        "/api/v1/portfolios/{portfolio_id}/allocation/sectors",
    ): "portafolios.leer",
    (
        "POST",
        "/api/v1/portfolios/{portfolio_id}/valuations",
    ): "portafolios.actualizar",
    (
        "GET",
        "/api/v1/portfolios/{portfolio_id}/valuations",
    ): "portafolios.leer",
    (
        "POST",
        "/api/v1/portfolios/{portfolio_id}/close",
    ): "portafolios.cerrar",
    (
        "POST",
        "/api/v1/portfolios/{portfolio_id}/positions",
    ): "portafolios.actualizar",
    (
        "GET",
        "/api/v1/portfolios/{portfolio_id}/positions",
    ): "portafolios.leer",
    (
        "PATCH",
        "/api/v1/portfolios/{portfolio_id}/positions/{position_id}",
    ): "portafolios.actualizar",
    (
        "DELETE",
        "/api/v1/portfolios/{portfolio_id}/positions/{position_id}",
    ): "portafolios.actualizar",

    (
        "POST",
        "/api/v1/simulations/configurations",
    ): "simulaciones.crear",
    (
        "GET",
        "/api/v1/simulations/configurations",
    ): "simulaciones.leer",
    (
        "GET",
        "/api/v1/simulations/configurations/{configuration_id}",
    ): "simulaciones.leer",
    (
        "PATCH",
        "/api/v1/simulations/configurations/{configuration_id}",
    ): "simulaciones.actualizar",
    (
        "POST",
        "/api/v1/simulations/configurations/{configuration_id}/archive",
    ): "simulaciones.archivar",
    (
        "POST",
        "/api/v1/simulations/configurations/{configuration_id}/assets",
    ): "simulaciones.actualizar",
    (
        "GET",
        "/api/v1/simulations/configurations/{configuration_id}/assets",
    ): "simulaciones.leer",
    (
        "PATCH",
        (
            "/api/v1/simulations/configurations/{configuration_id}"
            "/assets/{asset_id}"
        ),
    ): "simulaciones.actualizar",
    (
        "DELETE",
        (
            "/api/v1/simulations/configurations/{configuration_id}"
            "/assets/{asset_id}"
        ),
    ): "simulaciones.actualizar",
    (
        "GET",
        "/api/v1/simulations/configurations/{configuration_id}/distribution",
    ): "simulaciones.leer",
    (
        "POST",
        "/api/v1/simulations/configurations/{configuration_id}/ready",
    ): "simulaciones.actualizar",
    (
        "POST",
        "/api/v1/simulations/executions",
    ): "simulaciones.ejecutar",
    (
        "GET",
        "/api/v1/simulations/executions",
    ): "simulaciones.leer",
    (
        "GET",
        "/api/v1/simulations/executions/{execution_id}",
    ): "simulaciones.leer",
    (
        "GET",
        "/api/v1/simulations/executions/{execution_id}/result",
    ): "simulaciones.leer",
    (
        "POST",
        "/api/v1/simulations/executions/{execution_id}/cancel",
    ): "simulaciones.ejecutar",

    (
        "POST",
        "/api/v1/ai/analysis-requests",
    ): "analisis.solicitar",
    (
        "GET",
        "/api/v1/ai/analysis-requests/{request_id}",
    ): "analisis.leer",
    (
        "GET",
        "/api/v1/ai/models",
    ): "modelos.leer",
    (
        "PATCH",
        "/api/v1/ai/models/{model_id}/status",
    ): "modelos.administrar",
    (
        "POST",
        "/api/v1/ai/models/{model_id}/versions",
    ): "versiones_modelo.administrar",
    (
        "GET",
        "/api/v1/ai/models/{model_id}/versions",
    ): "versiones_modelo.leer",
    (
        "GET",
        "/api/v1/ai/models/code/{code}",
    ): "modelos.leer",
    (
        "GET",
        "/api/v1/ai/models/code/{code}/active-version",
    ): "versiones_modelo.leer",
    (
        "GET",
        "/api/v1/ai/models/{model_id}",
    ): "modelos.leer",
    (
        "GET",
        "/api/v1/ai/models/{model_id}/active-version",
    ): "versiones_modelo.leer",
    (
        "GET",
        "/api/v1/ai/versions/{version_id}",
    ): "versiones_modelo.leer",
    (
        "POST",
        "/api/v1/ai/versions/{version_id}/activate",
    ): "versiones_modelo.activar",
    (
        "POST",
        "/api/v1/ai/versions/{version_id}/deactivate",
    ): "versiones_modelo.activar",
    (
        "GET",
        "/api/v1/ai/analysis-requests/{request_id}/result",
    ): "analisis.leer",
    (
        "POST",
        "/api/v1/ai/sentiment-analysis-requests",
    ): "analisis.solicitar",
    (
        "POST",
        "/api/v1/ai/recommendation-requests",
    ): "analisis.solicitar",
    (
        "GET",
        "/api/v1/ai/recommendation-requests/{request_id}",
    ): "analisis.leer",
    (
        "GET",
        "/api/v1/ai/recommendation-requests/{request_id}/result",
    ): "analisis.leer",
    (
        "POST",
        "/api/v1/ai/integral-analysis-requests",
    ): "analisis.solicitar",
    (
        "GET",
        "/api/v1/ai/integral-analysis-requests/{request_id}",
    ): "analisis.leer",
    (
        "GET",
        "/api/v1/ai/integral-analysis-requests/{request_id}/result",
    ): "analisis.leer",

    (
        "GET",
        "/api/v1/news/assets/{asset_id}",
    ): "noticias.leer",
    (
        "POST",
        "/api/v1/news/assets/{asset_id}/sync",
    ): "noticias.cargar",

    (
        "GET",
        "/api/v1/notifications",
    ): "notificaciones.leer",
    (
        "GET",
        "/api/v1/notifications/unread-count",
    ): "notificaciones.leer",
    (
        "GET",
        "/api/v1/notifications/admin",
    ): "notificaciones.administrar",
    (
        "GET",
        "/api/v1/notifications/admin/{notification_id}",
    ): "notificaciones.administrar",
    (
        "PATCH",
        "/api/v1/notifications/admin/{notification_id}/cancel",
    ): "notificaciones.administrar",
    (
        "GET",
        "/api/v1/notifications/{notification_id}",
    ): "notificaciones.leer",
    (
        "PATCH",
        "/api/v1/notifications/{notification_id}/read",
    ): "notificaciones.leer",

    (
        "GET",
        "/api/v1/reports/assets",
    ): "reportes.leer",
    (
        "GET",
        "/api/v1/reports/portfolios",
    ): "reportes.leer",
    (
        "GET",
        "/api/v1/reports/simulations",
    ): "reportes.leer",
    (
        "GET",
        "/api/v1/reports/recommendations",
    ): "reportes.leer",
    (
        "GET",
        "/api/v1/reports/export/assets",
    ): "reportes.exportar",
    (
        "GET",
        "/api/v1/reports/export/portfolios",
    ): "reportes.exportar",
    (
        "GET",
        "/api/v1/reports/export/simulations",
    ): "reportes.exportar",
    (
        "GET",
        "/api/v1/reports/export/recommendations",
    ): "reportes.exportar",
    (
        "GET",
        "/api/v1/reports/admin/users",
    ): "reportes.administrar",
    (
        "GET",
        "/api/v1/reports/admin/audit",
    ): "reportes.administrar",
    (
        "GET",
        "/api/v1/reports/admin/jobs",
    ): "reportes.administrar",
    (
        "GET",
        "/api/v1/reports/admin/export/users",
    ): "reportes.administrar + reportes.exportar",
    (
        "GET",
        "/api/v1/reports/admin/export/audit",
    ): "reportes.administrar + reportes.exportar",
    (
        "GET",
        "/api/v1/reports/admin/export/jobs",
    ): "reportes.administrar + reportes.exportar",
}


PUBLIC_OPERATIONS = {
    (
        "GET",
        "/api/v1/health",
    ),
    (
        "GET",
        "/api/v1/health/live",
    ),
    (
        "GET",
        "/api/v1/health/ready",
    ),
    (
        "POST",
        "/api/v1/auth/register",
    ),
    (
        "POST",
        "/api/v1/auth/login",
    ),
    (
        "POST",
        "/api/v1/auth/refresh",
    ),
    (
        "POST",
        "/api/v1/auth/logout",
    ),
    (
        "GET",
        "/api/v1/profile/questionnaire",
    ),
}


def load_openapi() -> dict[str, Any]:
    if not OPENAPI_PATH.exists():
        raise FileNotFoundError(
            f"No existe el archivo OpenAPI: {OPENAPI_PATH}"
        )

    with OPENAPI_PATH.open(
        "r",
        encoding="utf-8",
    ) as openapi_file:
        return json.load(openapi_file)


def resolve_schema_name(
    schema: dict[str, Any] | None,
) -> str:
    if not schema:
        return "-"

    ref = schema.get("$ref")

    if isinstance(ref, str):
        return ref.rsplit("/", maxsplit=1)[-1]

    schema_type = schema.get("type")

    if schema_type == "array":
        item_schema = schema.get("items")

        return (
            f"list[{resolve_schema_name(item_schema)}]"
        )

    if schema_type:
        return str(schema_type)

    return "Inline schema"


def request_schema_name(
    operation: dict[str, Any],
) -> str:
    request_body = operation.get(
        "requestBody"
    )

    if not request_body:
        return "-"

    content = request_body.get(
        "content",
        {}
    )

    for media_type in (
        "application/json",
        "multipart/form-data",
        "application/x-www-form-urlencoded",
    ):
        media = content.get(media_type)

        if media:
            return resolve_schema_name(
                media.get("schema")
            )

    return "Request body"


def response_schema_name(
    operation: dict[str, Any],
) -> str:
    responses = operation.get(
        "responses",
        {}
    )

    success_codes = sorted(
        code
        for code in responses
        if str(code).startswith("2")
    )

    if not success_codes:
        return "-"

    response = responses[
        success_codes[0]
    ]

    content = response.get(
        "content",
        {}
    )

    if not content:
        return "-"

    for media_type in (
        "application/json",
        "text/csv",
    ):
        media = content.get(media_type)

        if media:
            return resolve_schema_name(
                media.get("schema")
            )

    return "Response body"


def status_codes(
    operation: dict[str, Any],
) -> str:
    responses = operation.get(
        "responses",
        {}
    )

    return ", ".join(
        str(code)
        for code in responses
    )


def authentication_requirement(
    method: str,
    path: str,
) -> str:
    key = (
        method,
        path,
    )

    if key in PUBLIC_OPERATIONS:
        return "Público"

    permission = PERMISSION_BY_OPERATION.get(
        key
    )

    if permission is None:
        return "REVISAR"

    return permission


def parameters_summary(
    operation: dict[str, Any],
) -> str:
    parameters = operation.get(
        "parameters",
        []
    )

    if not parameters:
        return "-"

    values: list[str] = []

    for parameter in parameters:
        name = parameter.get(
            "name",
            "?"
        )

        location = parameter.get(
            "in",
            "?"
        )

        required = (
            "req"
            if parameter.get(
                "required",
                False,
            )
            else "opt"
        )

        values.append(
            f"{name} ({location}, {required})"
        )

    return "; ".join(values)


def escape_markdown(
    value: object,
) -> str:
    return (
        str(value)
        .replace("|", "\\|")
        .replace("\n", " ")
    )


def generate_document(
    openapi: dict[str, Any],
) -> str:
    info = openapi.get(
        "info",
        {}
    )

    schemas = (
        openapi.get(
            "components",
            {}
        )
        .get(
            "schemas",
            {}
        )
    )

    security_schemes = (
        openapi.get(
            "components",
            {}
        )
        .get(
            "securitySchemes",
            {}
        )
    )

    lines: list[str] = [
        "# AlphaInvest AI — Referencia de API",
        "",
        "Documento generado automáticamente a partir de OpenAPI.",
        "",
        "## Información general",
        "",
        f"- **Nombre:** {info.get('title', '-')}",
        f"- **Versión:** {info.get('version', '-')}",
        "- **Base path:** `/api/v1`",
        "- **Swagger UI:** `/docs`",
        "- **ReDoc:** `/redoc`",
        "- **OpenAPI:** `/openapi.json`",
        f"- **Paths OpenAPI:** {len(openapi.get('paths', {}))}",
        f"- **Schemas:** {len(schemas)}",
        "",
        "## Autenticación",
        "",
        "AlphaInvest AI utiliza tokens de acceso Bearer.",
        "",
        "```http",
        "Authorization: Bearer <access_token>",
        "```",
        "",
        "Esquemas OpenAPI registrados:",
        "",
        "```json",
        json.dumps(
            security_schemes,
            indent=2,
            ensure_ascii=False,
        ),
        "```",
        "",
        "## Convenciones",
        "",
        "- `Público`: no requiere access token.",
        "- `Autenticado`: requiere sesión válida.",
        "- Cualquier código como `activos.leer` corresponde a un permiso RBAC.",
        "- Los endpoints administrativos pueden requerir más de un permiso.",
        "- Los recursos personales aplican control de propiedad por usuario.",
        "",
        "## Endpoints",
        "",
        "| Método | Ruta | Tag | Resumen | Acceso | Request | Response | Parámetros | Códigos |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    paths = openapi.get(
        "paths",
        {}
    )

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method not in HTTP_METHODS:
                continue

            http_method = (
                method.upper()
            )

            tags = ", ".join(
                operation.get(
                    "tags",
                    [],
                )
            )

            summary = operation.get(
                "summary",
                "-"
            )

            access = (
                authentication_requirement(
                    http_method,
                    path,
                )
            )

            request_schema = (
                request_schema_name(
                    operation
                )
            )

            response_schema = (
                response_schema_name(
                    operation
                )
            )

            parameters = (
                parameters_summary(
                    operation
                )
            )

            codes = status_codes(
                operation
            )

            cells = [
                http_method,
                f"`{path}`",
                tags or "-",
                summary,
                access,
                request_schema,
                response_schema,
                parameters,
                codes,
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

    lines.extend(
        [
            "",
            "## Schemas registrados",
            "",
        ]
    )

    for schema_name in sorted(
        schemas
    ):
        lines.append(
            f"- `{schema_name}`"
        )

    lines.extend(
        [
            "",
            "## Fuente",
            "",
            (
                "Este documento se genera a partir de "
                "`openapi_alphainvest.json`, obtenido de "
                "`GET /openapi.json` en una instancia real "
                "del backend."
            ),
            "",
            (
                "Los permisos RBAC se complementan con las "
                "dependencias reales de los módulos de "
                "AlphaInvest AI."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def validate_permissions(
    openapi: dict[str, Any],
) -> list[
    tuple[str, str]
]:
    missing: list[
        tuple[str, str]
    ] = []

    paths = openapi.get(
        "paths",
        {}
    )

    for path, path_item in paths.items():
        for method in path_item:
            if method not in HTTP_METHODS:
                continue

            key = (
                method.upper(),
                path,
            )

            if (
                key not in PUBLIC_OPERATIONS
                and key
                not in PERMISSION_BY_OPERATION
            ):
                missing.append(
                    key
                )

    return missing


def main() -> None:
    openapi = load_openapi()

    missing = validate_permissions(
        openapi
    )

    if missing:
        print(
            "ATENCIÓN: existen operaciones sin "
            "clasificación de seguridad:"
        )

        for method, path in missing:
            print(
                f"  {method} {path}"
            )

        raise SystemExit(1)

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = generate_document(
        openapi
    )

    OUTPUT_PATH.write_text(
        document,
        encoding="utf-8",
    )

    operation_count = sum(
        1
        for path_item in openapi[
            "paths"
        ].values()
        for method in path_item
        if method in HTTP_METHODS
    )

    print(
        "Documentación API generada correctamente."
    )
    print(
        f"Operaciones documentadas: {operation_count}"
    )
    print(
        f"Schemas registrados: "
        f"{len(openapi['components']['schemas'])}"
    )
    print(
        f"Archivo: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()