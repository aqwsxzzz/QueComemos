"""Reporting, blocking, and takedowns."""

from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from quecomemos.features.user import service as user_service

RECIPE = {
    "title": "Milanesas a la napolitana",
    "ingredients": [{"raw_text": "4 milanesas"}],
    "steps": [{"text": "Freír."}, {"text": "Cubrir con salsa y queso."}],
}


async def _account(client: AsyncClient, prefix: str, name: str) -> dict[str, Any]:
    response = await client.post(
        f"{prefix}/auth/register",
        json={
            "email": f"{name}@example.com",
            "password": "milanesas-napolitana-5",
            "display_name": name.capitalize(),
        },
    )
    body: dict[str, Any] = response.json()
    return body


def _auth(session: dict[str, Any]) -> dict[str, str]:
    return {"Authorization": f"Bearer {session['tokens']['access_token']}"}


async def _recipe(client: AsyncClient, prefix: str, session: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(f"{prefix}/recipes", json=RECIPE, headers=_auth(session))
    body: dict[str, Any] = response.json()
    return body


async def _make_maintainer(db: AsyncSession, email: str) -> None:
    user = await user_service.get_by_email(db, email)
    assert user is not None
    user.is_maintainer = True
    await db.commit()


# --- reports ------------------------------------------------------------------


async def test_anyone_signed_in_can_report_a_recipe(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)

    response = await client.post(
        f"{api_prefix}/reports",
        json={"target_type": "recipe", "target_id": recipe["id"], "reason": "spam"},
        headers=_auth(beto),
    )

    assert response.status_code == 201
    assert response.json()["status"] == "open"


async def test_reporting_requires_authentication(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)

    response = await client.post(
        f"{api_prefix}/reports",
        json={"target_type": "recipe", "target_id": recipe["id"], "reason": "spam"},
    )

    assert response.status_code == 401


async def test_reporting_something_that_does_not_exist_is_404(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")

    response = await client.post(
        f"{api_prefix}/reports",
        json={
            "target_type": "recipe",
            "target_id": "11111111-1111-1111-1111-111111111111",
            "reason": "spam",
        },
        headers=_auth(ana),
    )

    assert response.status_code == 404


async def test_the_report_queue_is_maintainer_only(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")

    response = await client.get(f"{api_prefix}/reports", headers=_auth(ana))

    assert response.status_code == 403


async def test_a_maintainer_can_read_and_resolve_the_queue(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    report = await client.post(
        f"{api_prefix}/reports",
        json={"target_type": "recipe", "target_id": recipe["id"], "reason": "abuse"},
        headers=_auth(beto),
    )
    await _make_maintainer(db, "beto@example.com")

    queue = await client.get(f"{api_prefix}/reports", headers=_auth(beto))
    assert queue.json()["meta"]["total"] == 1

    resolved = await client.patch(
        f"{api_prefix}/reports/{report.json()['id']}",
        json={"status": "dismissed"},
        headers=_auth(beto),
    )
    assert resolved.json()["status"] == "dismissed"


# --- blocks -------------------------------------------------------------------


async def test_blocking_hides_comments_in_both_directions(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    for session, body in ((ana, "Gracias!"), (beto, "Riquísimo")):
        await client.post(
            f"{api_prefix}/recipes/{recipe['id']}/comments",
            json={"body": body},
            headers=_auth(session),
        )

    await client.post(
        f"{api_prefix}/blocks", json={"blocked_id": beto["user"]["id"]}, headers=_auth(ana)
    )

    # Each side keeps their own comment and loses the other's. Hiding somebody's
    # own words from them would be a shadow ban, which is a different feature.
    as_ana = await client.get(f"{api_prefix}/recipes/{recipe['id']}/comments", headers=_auth(ana))
    assert [comment["body"] for comment in as_ana.json()["data"]] == ["Gracias!"]

    as_beto = await client.get(
        f"{api_prefix}/recipes/{recipe['id']}/comments", headers=_auth(beto)
    )
    assert [comment["body"] for comment in as_beto.json()["data"]] == ["Riquísimo"]

    # An anonymous reader is unaffected: a block is personal, not a takedown.
    anonymous = await client.get(f"{api_prefix}/recipes/{recipe['id']}/comments")
    assert anonymous.json()["meta"]["total"] == 2


async def test_blocking_severs_the_follow_in_both_directions(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    await client.put(f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana))
    await client.put(f"{api_prefix}/cooks/{ana['user']['id']}/follow", headers=_auth(beto))

    await client.post(
        f"{api_prefix}/blocks", json={"blocked_id": beto["user"]["id"]}, headers=_auth(ana)
    )

    assert (await client.get(f"{api_prefix}/me/following", headers=_auth(ana))).json()["meta"][
        "total"
    ] == 0
    assert (await client.get(f"{api_prefix}/me/following", headers=_auth(beto))).json()["meta"][
        "total"
    ] == 0


async def test_a_blocked_user_cannot_be_followed(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    await client.post(
        f"{api_prefix}/blocks", json={"blocked_id": beto["user"]["id"]}, headers=_auth(ana)
    )

    response = await client.put(
        f"{api_prefix}/cooks/{beto['user']['id']}/follow", headers=_auth(ana)
    )

    assert response.status_code == 422


async def test_a_blocked_user_cannot_comment_on_the_blocker(
    client: AsyncClient, api_prefix: str
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    await client.post(
        f"{api_prefix}/blocks", json={"blocked_id": beto["user"]["id"]}, headers=_auth(ana)
    )

    response = await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "hola de nuevo"},
        headers=_auth(beto),
    )

    assert response.status_code == 403


async def test_blocking_yourself_is_rejected(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")

    response = await client.post(
        f"{api_prefix}/blocks", json={"blocked_id": ana["user"]["id"]}, headers=_auth(ana)
    )

    assert response.status_code == 422


async def test_unblocking_restores_visibility(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "Riquísimo"},
        headers=_auth(beto),
    )
    await client.post(
        f"{api_prefix}/blocks", json={"blocked_id": beto["user"]["id"]}, headers=_auth(ana)
    )

    await client.delete(f"{api_prefix}/blocks/{beto['user']['id']}", headers=_auth(ana))

    listing = await client.get(f"{api_prefix}/recipes/{recipe['id']}/comments", headers=_auth(ana))
    assert listing.json()["meta"]["total"] == 1


# --- takedowns ----------------------------------------------------------------


async def test_takedown_is_maintainer_only(client: AsyncClient, api_prefix: str) -> None:
    ana = await _account(client, api_prefix, "ana")
    recipe = await _recipe(client, api_prefix, ana)

    response = await client.delete(
        f"{api_prefix}/moderation/recipes/{recipe['id']}", headers=_auth(ana)
    )

    assert response.status_code == 403


async def test_removing_a_recipe_also_removes_its_comments(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    recipe = await _recipe(client, api_prefix, ana)
    await client.post(
        f"{api_prefix}/recipes/{recipe['id']}/comments",
        json={"body": "spam"},
        headers=_auth(beto),
    )
    await _make_maintainer(db, "beto@example.com")

    removed = await client.delete(
        f"{api_prefix}/moderation/recipes/{recipe['id']}", headers=_auth(beto)
    )

    assert removed.status_code == 204
    assert (await client.get(f"{api_prefix}/recipes/{recipe['id']}")).status_code == 404
    assert (await client.get(f"{api_prefix}/recipes")).json()["meta"]["total"] == 0


async def test_removing_an_author_removes_everything_they_published(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    await _recipe(client, api_prefix, ana)
    await _recipe(client, api_prefix, ana)
    await _make_maintainer(db, "beto@example.com")

    removed = await client.delete(
        f"{api_prefix}/moderation/users/{ana['user']['id']}", headers=_auth(beto)
    )

    assert removed.status_code == 204
    assert (await client.get(f"{api_prefix}/recipes")).json()["meta"]["total"] == 0
    assert (await client.get(f"{api_prefix}/users/{ana['user']['id']}")).status_code == 404


async def test_removing_an_author_kills_their_live_session(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    await _make_maintainer(db, "beto@example.com")

    await client.delete(f"{api_prefix}/moderation/users/{ana['user']['id']}", headers=_auth(beto))

    assert (await client.get(f"{api_prefix}/users/me", headers=_auth(ana))).status_code == 401
    refreshed = await client.post(
        f"{api_prefix}/auth/refresh", json={"refresh_token": ana["tokens"]["refresh_token"]}
    )
    assert refreshed.status_code == 401


async def test_a_removed_author_cannot_log_back_in(
    client: AsyncClient, api_prefix: str, db: AsyncSession
) -> None:
    ana = await _account(client, api_prefix, "ana")
    beto = await _account(client, api_prefix, "beto")
    await _make_maintainer(db, "beto@example.com")

    await client.delete(f"{api_prefix}/moderation/users/{ana['user']['id']}", headers=_auth(beto))

    response = await client.post(
        f"{api_prefix}/auth/login",
        json={"email": "ana@example.com", "password": "milanesas-napolitana-5"},
    )

    assert response.status_code == 401
