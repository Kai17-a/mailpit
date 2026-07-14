import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request, Response

app = FastAPI(
    title="Mailpit Discord Webhook",
    docs_url=None,
    redoc_url=None,
)

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
MAILPIT_PUBLIC_URL = os.getenv(
    "MAILPIT_PUBLIC_URL",
    "http://localhost:8025",
).rstrip("/")


def format_address(value: Any) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        name = value.get("Name") or value.get("name") or ""
        address = value.get("Address") or value.get("address") or ""

        if name and address:
            return f"{name} <{address}>"

        return address or name

    if isinstance(value, list):
        addresses = [format_address(item) for item in value]
        return ", ".join(address for address in addresses if address)

    return str(value or "")


@app.post("/mail", status_code=204)
async def receive_mail(request: Request) -> Response:
    try:
        data = await request.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        ) from exc

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="JSON payload must be an object",
        )

    subject = data.get("Subject") or data.get("subject") or "件名なし"
    sender = format_address(data.get("From") or data.get("from"))
    recipients = format_address(data.get("To") or data.get("to"))
    snippet = data.get("Snippet") or data.get("snippet") or "本文なし"

    discord_payload = {
        "username": "Mailpit",
        "embeds": [
            {
                "title": str(subject)[:256],
                "fields": [
                    {
                        "name": "送信元",
                        "value": sender[:1024] or "不明",
                        "inline": False,
                    },
                    {
                        "name": "宛先",
                        "value": recipients[:1024] or "不明",
                        "inline": False,
                    },
                    {
                        "name": "本文",
                        "value": str(snippet)[:1024] or "本文なし",
                        "inline": False,
                    },
                    {
                        "name": "Mailpit",
                        "value": f"[メールを確認する]({MAILPIT_PUBLIC_URL})",
                        "inline": False,
                    },
                ],
            }
        ],
        "allowed_mentions": {
            "parse": [],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                DISCORD_WEBHOOK_URL,
                json=discord_payload,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Failed to send Discord webhook",
        ) from exc

    return Response(status_code=204)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
