#!/usr/bin/env python3
"""Smoke live da API: GET /health e GET /lotteries.

Uso:
  python scripts/smoke_api.py
  API_BASE_URL=https://api.exemplo.com python scripts/smoke_api.py
"""

from __future__ import annotations

import os
import sys

try:
    import httpx
except ImportError:
    print("ERRO: httpx não instalado. Use: pip install -e \".[api]\"", file=sys.stderr)
    sys.exit(2)


def _base_url() -> str:
    return os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def check_health(client: httpx.Client, base: str) -> None:
    url = f"{base}/health"
    response = client.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"GET /health → HTTP {response.status_code}: {response.text[:200]}")
    payload = response.json()
    if payload.get("status") != "ok":
        raise RuntimeError(f"GET /health → status inesperado: {payload!r}")
    print(f"OK  GET /health → status=ok (database.exists={payload.get('database', {}).get('exists')})")


def check_lotteries(client: httpx.Client, base: str) -> None:
    url = f"{base}/lotteries"
    response = client.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"GET /lotteries → HTTP {response.status_code}: {response.text[:200]}")
    payload = response.json()
    items = payload if isinstance(payload, list) else payload.get("lotteries") or payload.get("items")
    if not isinstance(items, list) or len(items) == 0:
        raise RuntimeError(f"GET /lotteries → lista vazia ou formato inválido: {payload!r}")
    print(f"OK  GET /lotteries → {len(items)} modalidade(s)")


def main() -> int:
    base = _base_url()
    print(f"Smoke API → {base}")
    try:
        with httpx.Client(timeout=15.0) as client:
            check_health(client, base)
            check_lotteries(client, base)
    except Exception as exc:
        print(f"FALHA: {exc}", file=sys.stderr)
        return 1
    print("Smoke API concluído com sucesso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
