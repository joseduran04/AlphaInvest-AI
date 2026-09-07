from __future__ import annotations

import asyncio
import json
import secrets
import string
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text

from alphainvest.infrastructure.database.session import engine

BASE_URL = "http://127.0.0.1:8000/api/v1"

EMAIL: str | None = None
PASSWORD: str | None = None
USER_ID: str | None = None
PORTFOLIO_ID: str | None = None
CONFIGURATION_ID: str | None = None
EXECUTION_ID: str | None = None

ACCESS_TOKEN: str | None = None
REFRESH_TOKEN: str | None = None


def random_password() -> str:
    alphabet = (
        string.ascii_letters
        + string.digits
        + "!@#$%^&*"
    )

    return (
        "Aa1!"
        + "".join(
            secrets.choice(alphabet)
            for _ in range(20)
        )
    )


def unwrap(payload: Any) -> Any:
    if (
        isinstance(payload, dict)
        and "success" in payload
        and "data" in payload
    ):
        return payload["data"]

    return payload


def request(
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    token: str | None = None,
    expected: tuple[int, ...] = (200,),
) -> tuple[int, Any]:
    url = f"{BASE_URL}{path}"

    headers = {
        "Accept": "application/json",
        "User-Agent": "AlphaInvest-E2E-Supabase/1.0",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    encoded_body: bytes | None = None

    if body is not None:
        headers["Content-Type"] = "application/json"
        encoded_body = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=encoded_body,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(
            req,
            timeout=30,
        ) as response:
            status = response.status
            raw = response.read()

    except urllib.error.HTTPError as exc:
        raw = exc.read()

        try:
            payload = json.loads(
                raw.decode("utf-8")
            )
        except Exception:
            payload = raw.decode(
                "utf-8",
                errors="replace",
            )

        print(
            f"[FAIL] {method} {path}"
            f" -> HTTP {exc.code}"
        )
        print(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
            if isinstance(payload, (dict, list))
            else payload
        )

        raise RuntimeError(
            f"HTTP inesperado: {exc.code}"
        ) from exc

    if raw:
        try:
            payload = json.loads(
                raw.decode("utf-8")
            )
        except json.JSONDecodeError:
            payload = raw.decode(
                "utf-8",
                errors="replace",
            )
    else:
        payload = None

    if status not in expected:
        raise RuntimeError(
            f"{method} {path}: "
            f"HTTP {status}; esperado {expected}"
        )

    return status, unwrap(payload)


def pass_step(
    name: str,
    detail: str | None = None,
) -> None:
    if detail:
        print(f"[PASS] {name}: {detail}")
    else:
        print(f"[PASS] {name}")


def require_dict(
    value: Any,
    name: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError(
            f"{name}: se esperaba un objeto JSON"
        )

    return value


def require_list(
    value: Any,
    name: str,
) -> list[Any]:
    if not isinstance(value, list):
        raise RuntimeError(
            f"{name}: se esperaba una lista JSON"
        )

    return value


def list_items(
    value: Any,
    name: str,
) -> list[Any]:
    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        items = value.get("items")

        if isinstance(items, list):
            return items

    raise RuntimeError(
        f"{name}: no se encontró una lista "
        "ni un campo items"
    )


async def cleanup_database() -> None:
    global USER_ID
    global PORTFOLIO_ID
    global CONFIGURATION_ID
    global EXECUTION_ID
    global EMAIL

    print("\n--- CLEANUP E2E ---")

    async with engine.begin() as conn:
        if EXECUTION_ID:
            await conn.execute(
                text(
                    """
                    DELETE FROM simulation.ejecuciones
                    WHERE id = :id
                    """
                ),
                {"id": UUID(EXECUTION_ID)},
            )

        if CONFIGURATION_ID:
            candidate_tables = (
                "configuracion_activos",
                "configuraciones_activos",
                "activos_configuracion",
            )

            for table_name in candidate_tables:
                exists = await conn.scalar(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = 'simulation'
                              AND table_name = :table_name
                        )
                        """
                    ),
                    {"table_name": table_name},
                )

                if exists:
                    columns = (
                        await conn.execute(
                            text(
                                """
                                SELECT column_name
                                FROM information_schema.columns
                                WHERE table_schema = 'simulation'
                                  AND table_name = :table_name
                                """
                            ),
                            {"table_name": table_name},
                        )
                    ).scalars().all()

                    fk_column = None

                    for candidate in (
                        "configuracion_id",
                        "configuration_id",
                    ):
                        if candidate in columns:
                            fk_column = candidate
                            break

                    if fk_column:
                        await conn.execute(
                            text(
                                f"""
                                DELETE FROM simulation.{table_name}
                                WHERE {fk_column} = :id
                                """
                            ),
                            {
                                "id": UUID(
                                    CONFIGURATION_ID
                                )
                            },
                        )

            await conn.execute(
                text(
                    """
                    DELETE FROM simulation.configuraciones
                    WHERE id = :id
                    """
                ),
                {"id": UUID(CONFIGURATION_ID)},
            )

        if PORTFOLIO_ID:
            candidate_tables = (
                "valoraciones_portafolio",
                "valoraciones",
                "posiciones",
            )

            for table_name in candidate_tables:
                exists = await conn.scalar(
                    text(
                        """
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_schema = 'portfolio'
                              AND table_name = :table_name
                        )
                        """
                    ),
                    {"table_name": table_name},
                )

                if not exists:
                    continue

                columns = (
                    await conn.execute(
                        text(
                            """
                            SELECT column_name
                            FROM information_schema.columns
                            WHERE table_schema = 'portfolio'
                              AND table_name = :table_name
                            """
                        ),
                        {"table_name": table_name},
                    )
                ).scalars().all()

                if "portafolio_id" in columns:
                    await conn.execute(
                        text(
                            f"""
                            DELETE FROM portfolio.{table_name}
                            WHERE portafolio_id = :id
                            """
                        ),
                        {
                            "id": UUID(
                                PORTFOLIO_ID
                            )
                        },
                    )

            await conn.execute(
                text(
                    """
                    DELETE FROM portfolio.portafolios
                    WHERE id = :id
                    """
                ),
                {"id": UUID(PORTFOLIO_ID)},
            )

        if USER_ID:
            uid = UUID(USER_ID)

            cleanup_statements = (
                """
                DELETE FROM ai.recomendaciones
                WHERE usuario_id = :user_id
                """,
                """
                DELETE FROM ai.solicitudes_analisis
                WHERE usuario_id = :user_id
                """,
                """
                DELETE FROM profile.perfiles_riesgo
                WHERE usuario_id = :user_id
                """,
                """
                DELETE FROM profile.evaluaciones_riesgo
                WHERE usuario_id = :user_id
                """,
                """
                DELETE FROM operation.notificaciones
                WHERE usuario_id = :user_id
                """,
                """
                DELETE FROM app_auth.aceptaciones_terminos
                WHERE usuario_id = :user_id
                """,
            )

            for statement in cleanup_statements:
                await conn.execute(
                    text(statement),
                    {"user_id": uid},
                )

            await conn.execute(
                text(
                    """
                    DELETE FROM app_auth.usuarios
                    WHERE id = :user_id
                    """
                ),
                {"user_id": uid},
            )

    async with engine.connect() as conn:
        if EMAIL:
            remaining = await conn.scalar(
                text(
                    """
                    SELECT COUNT(*)
                    FROM app_auth.usuarios
                    WHERE correo = :email
                    """
                ),
                {"email": EMAIL},
            )

            if remaining != 0:
                raise RuntimeError(
                    "El usuario E2E no pudo "
                    "eliminarse completamente"
                )

    pass_step(
        "Cleanup",
        "usuario E2E eliminado",
    )


def run_e2e() -> None:
    global EMAIL
    global PASSWORD
    global USER_ID
    global PORTFOLIO_ID
    global CONFIGURATION_ID
    global EXECUTION_ID
    global ACCESS_TOKEN
    global REFRESH_TOKEN

    suffix = secrets.token_hex(6)

    EMAIL = (
        f"e2e.supabase.{suffix}"
        "@example.com"
    )
    PASSWORD = random_password()

    print("=" * 72)
    print("AlphaInvest AI - E2E Supabase")
    print("=" * 72)
    print(f"Usuario temporal: {EMAIL}")
    print(
        "La contraseña temporal no se "
        "mostrará ni se almacenará."
    )
    print()

    status, health = request(
        "GET",
        "/health/ready",
        expected=(200,),
    )

    health_data = require_dict(
        health,
        "health",
    )

    if health_data.get("database") != "up":
        raise RuntimeError(
            "PostgreSQL no está disponible"
        )

    if health_data.get("mongodb") != "up":
        raise RuntimeError(
            "MongoDB no está disponible"
        )

    pass_step(
        "Health readiness",
        f"HTTP {status}",
    )

    _, registered = request(
        "POST",
        "/auth/register",
        body={
            "nombres": "E2E",
            "apellidos": "Supabase",
            "correo": EMAIL,
            "password": PASSWORD,
            "version_terminos": "E2E-1.0",
            "version_privacidad": "E2E-1.0",
        },
        expected=(201,),
    )

    registered_data = require_dict(
        registered,
        "register",
    )

    USER_ID = str(registered_data["id"])

    pass_step(
        "Register",
        USER_ID,
    )

    _, login = request(
        "POST",
        "/auth/login",
        body={
            "correo": EMAIL,
            "password": PASSWORD,
        },
        expected=(200,),
    )

    login_data = require_dict(
        login,
        "login",
    )

    ACCESS_TOKEN = str(
        login_data["access_token"]
    )
    REFRESH_TOKEN = str(
        login_data["refresh_token"]
    )

    pass_step("Login + JWT")

    _, me = request(
        "GET",
        "/auth/me",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    me_data = require_dict(
        me,
        "auth/me",
    )

    if str(me_data["id"]) != USER_ID:
        raise RuntimeError(
            "/auth/me devolvió otro usuario"
        )

    pass_step(
        "Auth /me",
        str(me_data.get("correo")),
    )

    _, questionnaire = request(
        "GET",
        "/profile/questionnaire",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    questionnaire_data = require_dict(
        questionnaire,
        "questionnaire",
    )

    questions = require_list(
        questionnaire_data.get(
            "preguntas",
            []
        ),
        "questionnaire.preguntas",
    )

    if not questions:
        raise RuntimeError(
            "El cuestionario no tiene preguntas"
        )

    answers: list[dict[str, str]] = []

    for question_raw in questions:
        question = require_dict(
            question_raw,
            "question",
        )

        options = require_list(
            question.get("opciones", []),
            "question.opciones",
        )

        if not options:
            if question.get("obligatoria"):
                raise RuntimeError(
                    "Pregunta obligatoria "
                    "sin opciones"
                )

            continue

        option = require_dict(
            options[0],
            "option",
        )

        answers.append(
            {
                "question_id": str(
                    question["id"]
                ),
                "option_id": str(
                    option["id"]
                ),
            }
        )

    if not answers:
        raise RuntimeError(
            "No pudieron generarse respuestas"
        )

    pass_step(
        "Questionnaire",
        f"{len(questions)} preguntas",
    )

    _, evaluation = request(
        "POST",
        "/profile/evaluations",
        token=ACCESS_TOKEN,
        body={
            "questionnaire_id": str(
                questionnaire_data["id"]
            ),
            "answers": answers,
        },
        expected=(200, 201),
    )

    evaluation_data = require_dict(
        evaluation,
        "risk evaluation",
    )

    pass_step(
        "Risk evaluation",
        str(
            evaluation_data.get(
                "classification",
                "creada",
            )
        ),
    )

    request(
        "GET",
        "/profile/current",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    pass_step("Current risk profile")

    _, assets_response = request(
        "GET",
        "/market/assets?limit=20&offset=0",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    assets = list_items(
        assets_response,
        "market assets",
    )

    if not assets:
        raise RuntimeError(
            "No existen activos disponibles"
        )

    asset = require_dict(
        assets[0],
        "asset",
    )

    asset_id = str(asset["id"])

    pass_step(
        "Market assets",
        f"{len(assets)} obtenidos",
    )

    request(
        "GET",
        f"/market/assets/{asset_id}",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    pass_step(
        "Market asset detail",
        asset_id,
    )

    _, portfolio = request(
        "POST",
        "/portfolios",
        token=ACCESS_TOKEN,
        body={
            "nombre": (
                f"E2E Supabase {suffix}"
            ),
            "descripcion": (
                "Portafolio temporal "
                "de validación E2E"
            ),
            "moneda_base": "USD",
            "capital_inicial": "10000",
            "tipo": "VIRTUAL",
        },
        expected=(200, 201),
    )

    portfolio_data = require_dict(
        portfolio,
        "portfolio",
    )

    PORTFOLIO_ID = str(
        portfolio_data["id"]
    )

    pass_step(
        "Portfolio creation",
        PORTFOLIO_ID,
    )

    request(
        "GET",
        f"/portfolios/{PORTFOLIO_ID}",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    request(
        "GET",
        "/portfolios?limit=50&offset=0",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    pass_step(
        "Portfolio ownership",
    )

    today = date.today()

    simulation_start = (
        today - timedelta(days=90)
    )
    simulation_end = (
        today - timedelta(days=1)
    )

    _, configuration = request(
        "POST",
        "/simulations/configurations",
        token=ACCESS_TOKEN,
        body={
            "portafolio_id": PORTFOLIO_ID,
            "nombre": (
                f"E2E HISTORICA {suffix}"
            ),
            "descripcion": (
                "Configuración temporal "
                "de validación Supabase"
            ),
            "tipo_simulacion": "HISTORICA",
            "capital_inicial": "10000",
            "moneda_base": "USD",
            "fecha_inicio": (
                simulation_start.isoformat()
            ),
            "fecha_fin": (
                simulation_end.isoformat()
            ),
            "aportacion_periodica": "0",
            "comision_porcentaje": "0",
            "numero_escenarios": 1,
        },
        expected=(200, 201),
    )

    configuration_data = require_dict(
        configuration,
        "simulation configuration",
    )

    CONFIGURATION_ID = str(
        configuration_data["id"]
    )

    pass_step(
        "Simulation configuration",
        CONFIGURATION_ID,
    )

    request(
        "POST",
        (
            "/simulations/configurations/"
            f"{CONFIGURATION_ID}/assets"
        ),
        token=ACCESS_TOKEN,
        body={
            "activo_id": asset_id,
            "porcentaje_asignado": "100",
            "monto_inicial": "10000",
            "orden": 1,
        },
        expected=(200, 201),
    )

    pass_step(
        "Simulation allocation",
        "100 %",
    )

    _, distribution = request(
        "GET",
        (
            "/simulations/configurations/"
            f"{CONFIGURATION_ID}/distribution"
        ),
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    distribution_data = require_dict(
        distribution,
        "simulation distribution",
    )

    if not distribution_data.get(
        "distribucion_valida"
    ):
        raise RuntimeError(
            "La distribución no quedó válida"
        )

    pass_step(
        "Simulation distribution",
        "válida",
    )

    _, ready = request(
        "POST",
        (
            "/simulations/configurations/"
            f"{CONFIGURATION_ID}/ready"
        ),
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    ready_data = require_dict(
        ready,
        "simulation ready",
    )

    if (
        str(ready_data.get("estado"))
        != "LISTA"
    ):
        raise RuntimeError(
            "La configuración no quedó LISTA"
        )

    pass_step(
        "Simulation ready",
        "LISTA",
    )

    _, execution = request(
        "POST",
        "/simulations/executions",
        token=ACCESS_TOKEN,
        body={
            "configuracion_id": (
                CONFIGURATION_ID
            )
        },
        expected=(200, 201, 202),
    )

    execution_data = require_dict(
        execution,
        "simulation execution",
    )

    EXECUTION_ID = str(
        execution_data["id"]
    )

    pass_step(
        "Simulation execution",
        EXECUTION_ID,
    )

    request(
        "GET",
        (
            "/simulations/executions/"
            f"{EXECUTION_ID}"
        ),
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    pass_step(
        "Simulation execution detail",
    )

    request(
        "POST",
        (
            "/simulations/executions/"
            f"{EXECUTION_ID}/cancel"
        ),
        token=ACCESS_TOKEN,
        expected=(200, 204),
    )

    pass_step(
        "Simulation cancellation",
    )

    _, notifications = request(
        "GET",
        "/notifications?limit=20&offset=0",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    notification_items = list_items(
        notifications,
        "notifications",
    )

    pass_step(
        "Notifications",
        f"{len(notification_items)} obtenidas",
    )

    request(
        "GET",
        "/notifications/unread-count",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    pass_step(
        "Notification unread count",
    )

    _, report_assets = request(
        "GET",
        "/reports/assets?limit=20&offset=0",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    report_asset_items = list_items(
        report_assets,
        "report assets",
    )

    pass_step(
        "Report assets",
        f"{len(report_asset_items)} filas",
    )

    _, report_portfolios = request(
        "GET",
        "/reports/portfolios?limit=20&offset=0",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    report_portfolio_items = list_items(
        report_portfolios,
        "report portfolios",
    )

    if not any(
        isinstance(item, dict)
        and str(item.get("portfolio_id"))
        == PORTFOLIO_ID
        for item in report_portfolio_items
    ):
        print(
            "[WARN] El reporte de portafolios "
            "respondió correctamente, pero no "
            "se localizó por id en la primera "
            "página."
        )

    pass_step(
        "Report portfolios",
        f"{len(report_portfolio_items)} filas",
    )

    request(
        "GET",
        "/reports/simulations?limit=20&offset=0",
        token=ACCESS_TOKEN,
        expected=(200,),
    )

    pass_step(
        "Report simulations",
    )

    _, refreshed = request(
        "POST",
        "/auth/refresh",
        body={
            "refresh_token": REFRESH_TOKEN
        },
        expected=(200,),
    )

    refreshed_data = require_dict(
        refreshed,
        "refresh",
    )

    ACCESS_TOKEN = str(
        refreshed_data["access_token"]
    )

    new_refresh_token = refreshed_data.get(
        "refresh_token"
    )

    if new_refresh_token:
        REFRESH_TOKEN = str(
            new_refresh_token
        )

    pass_step(
        "Refresh token",
    )

    request(
        "POST",
        "/auth/logout",
        body={
            "refresh_token": REFRESH_TOKEN
        },
        expected=(200, 204),
    )

    pass_step(
        "Logout",
    )


async def main() -> int:
    failure: BaseException | None = None

    try:
        run_e2e()

    except BaseException as exc:
        failure = exc

        print()
        print("=" * 72)
        print("E2E FALLÓ")
        print("=" * 72)
        print(
            f"{type(exc).__name__}: {exc}"
        )

    finally:
        try:
            await cleanup_database()

        except BaseException as cleanup_exc:
            print()
            print("[FAIL] CLEANUP")
            print(
                f"{type(cleanup_exc).__name__}: "
                f"{cleanup_exc}"
            )

            if EMAIL:
                print(
                    "Usuario temporal que debe "
                    "revisarse manualmente:"
                )
                print(EMAIL)

            failure = (
                failure
                if failure is not None
                else cleanup_exc
            )

        await engine.dispose()

    if failure is not None:
        return 1

    print()
    print("=" * 72)
    print("E2E SUPABASE COMPLETADO")
    print("=" * 72)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))