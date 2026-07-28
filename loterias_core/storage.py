"""Persistência SQLite local — uma base compartilhada entre API e Streamlit."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

DEFAULT_DB_PATH = "app/data/loterias.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS lottery_metadata (
    lottery_key TEXT PRIMARY KEY,
    last_update TEXT NOT NULL,
    last_concurso INTEGER,
    total_records INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lottery_key TEXT NOT NULL,
    concurso INTEGER,
    draw_index INTEGER NOT NULL DEFAULT 0,
    jogo TEXT NOT NULL,
    extra_data TEXT,
    UNIQUE (lottery_key, concurso, draw_index)
);

CREATE INDEX IF NOT EXISTS idx_draws_lottery_key ON draws (lottery_key);
CREATE INDEX IF NOT EXISTS idx_draws_concurso ON draws (lottery_key, concurso);
"""


def get_db_path() -> str:
    """Caminho do arquivo SQLite (configurável via LOTTERIAS_DB_PATH)."""
    return os.environ.get("LOTTERIAS_DB_PATH", DEFAULT_DB_PATH)


def init_db(db_path: str | None = None) -> None:
    """Cria tabelas e índices se ainda não existirem."""
    path = db_path or get_db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as conn:
        conn.executescript(_SCHEMA)
        conn.commit()


@contextmanager
def _connect(db_path: str | None = None) -> Iterator[sqlite3.Connection]:
    path = db_path or get_db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        yield conn
    finally:
        conn.close()


def get_database_info(db_path: str | None = None) -> dict[str, Any]:
    """Metadados do arquivo de banco para /health."""
    path = Path(db_path or get_db_path())
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
            "last_update": None,
            "size_bytes": None,
        }
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
    return {
        "exists": True,
        "path": str(path),
        "last_update": mtime,
        "size_bytes": path.stat().st_size,
    }


def _now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def _serialize_jogo(jogo: Any) -> str:
    return json.dumps(jogo, ensure_ascii=False)


def _deserialize_jogo(raw: str) -> Any:
    return json.loads(raw)


def _serialize_extra(extra: dict[str, Any]) -> str | None:
    if not extra:
        return None
    return json.dumps(extra, ensure_ascii=False)


def _deserialize_extra(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    return json.loads(raw)


def _extract_concurso(row: dict[str, Any]) -> int | None:
    for key in ("concurso",):
        val = row.get(key)
        if val is None or (isinstance(val, float) and str(val) == "nan"):
            continue
        try:
            return int(val)
        except (TypeError, ValueError):
            continue
    return None


def _row_to_draw_values(
    lottery_key: str,
    row: dict[str, Any],
    *,
    draw_index: int = 0,
) -> tuple[str, int | None, int, str, str | None]:
    jogo = row.get("jogo")
    if jogo is None:
        raise ValueError("Linha sem coluna 'jogo'")

    extra: dict[str, Any] = {}
    for key, val in row.items():
        if key in ("jogo", "concurso", "draw_index"):
            continue
        if val is not None and not (isinstance(val, float) and str(val) == "nan"):
            extra[key] = val

    concurso = _extract_concurso(row)
    idx = int(row.get("draw_index", draw_index))
    return (
        lottery_key,
        concurso,
        idx,
        _serialize_jogo(jogo),
        _serialize_extra(extra),
    )


def _replace_draws(
    conn: sqlite3.Connection,
    lottery_key: str,
    rows: list[tuple[str, int | None, int, str, str | None]],
) -> int:
    conn.execute("DELETE FROM draws WHERE lottery_key = ?", (lottery_key,))
    conn.executemany(
        """
        INSERT INTO draws (lottery_key, concurso, draw_index, jogo, extra_data)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


def _insert_draws_ignore_conflict(
    conn: sqlite3.Connection,
    rows: list[tuple[str, int | None, int, str, str | None]],
) -> int:
    before = conn.total_changes
    conn.executemany(
        """
        INSERT OR IGNORE INTO draws (lottery_key, concurso, draw_index, jogo, extra_data)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )
    return conn.total_changes - before


def _update_metadata(
    conn: sqlite3.Connection,
    lottery_key: str,
    total_records: int,
    last_concurso: int | None,
) -> None:
    conn.execute(
        """
        INSERT INTO lottery_metadata (lottery_key, last_update, last_concurso, total_records)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(lottery_key) DO UPDATE SET
            last_update = excluded.last_update,
            last_concurso = excluded.last_concurso,
            total_records = excluded.total_records
        """,
        (lottery_key, _now_iso(), last_concurso, total_records),
    )


def _max_concurso(conn: sqlite3.Connection, lottery_key: str) -> int | None:
    row = conn.execute(
        "SELECT MAX(concurso) AS mx FROM draws WHERE lottery_key = ? AND concurso IS NOT NULL",
        (lottery_key,),
    ).fetchone()
    if row is None or row["mx"] is None:
        return None
    return int(row["mx"])


def save_draws_full(
    lottery_key: str,
    records: list[dict[str, Any]],
    *,
    db_path: str | None = None,
) -> int:
    """Substitui todos os sorteios de uma modalidade (upload manual / importação completa)."""
    init_db(db_path)
    draw_rows: list[tuple[str, int | None, int, str, str | None]] = []
    for i, row in enumerate(records):
        draw_rows.append(_row_to_draw_values(lottery_key, row, draw_index=i))

    with _connect(db_path) as conn:
        total = _replace_draws(conn, lottery_key, draw_rows)
        last_concurso = _max_concurso(conn, lottery_key)
        _update_metadata(conn, lottery_key, total, last_concurso)
        conn.commit()
    return total


def save_draws_incremental(
    lottery_key: str,
    records: list[dict[str, Any]],
    *,
    db_path: str | None = None,
) -> int:
    """
    Insere apenas concursos novos (concurso > last_concurso).
    Se não houver coluna concurso, faz replace completo quando há mais registros.
    """
    init_db(db_path)
    with _connect(db_path) as conn:
        meta = conn.execute(
            "SELECT last_concurso, total_records FROM lottery_metadata WHERE lottery_key = ?",
            (lottery_key,),
        ).fetchone()
        last_concurso = int(meta["last_concurso"]) if meta and meta["last_concurso"] is not None else None

        has_concurso = any(_extract_concurso(r) is not None for r in records)
        if not has_concurso:
            existing_count = int(meta["total_records"]) if meta else 0
            if len(records) <= existing_count:
                return 0
            draw_rows = [_row_to_draw_values(lottery_key, r, draw_index=i) for i, r in enumerate(records)]
            total = _replace_draws(conn, lottery_key, draw_rows)
            last_concurso = _max_concurso(conn, lottery_key)
            _update_metadata(conn, lottery_key, total, last_concurso)
            conn.commit()
            return total - existing_count if existing_count else total

        new_rows: list[tuple[str, int | None, int, str, str | None]] = []
        for i, row in enumerate(records):
            concurso = _extract_concurso(row)
            if last_concurso is not None and concurso is not None and concurso <= last_concurso:
                continue
            new_rows.append(_row_to_draw_values(lottery_key, row, draw_index=i))

        if not new_rows:
            conn.commit()
            return 0

        inserted = _insert_draws_ignore_conflict(conn, new_rows)
        total = conn.execute(
            "SELECT COUNT(*) AS c FROM draws WHERE lottery_key = ?",
            (lottery_key,),
        ).fetchone()["c"]
        last_concurso = _max_concurso(conn, lottery_key)
        _update_metadata(conn, lottery_key, int(total), last_concurso)
        conn.commit()
        return inserted


def load_draws(
    lottery_key: str,
    *,
    db_path: str | None = None,
) -> list[dict[str, Any]]:
    """Carrega sorteios de uma modalidade como lista de dicts."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT concurso, draw_index, jogo, extra_data
            FROM draws
            WHERE lottery_key = ?
            ORDER BY COALESCE(concurso, id), draw_index
            """,
            (lottery_key,),
        ).fetchall()

    records: list[dict[str, Any]] = []
    for row in rows:
        rec: dict[str, Any] = {"jogo": _deserialize_jogo(row["jogo"])}
        if row["concurso"] is not None:
            rec["concurso"] = row["concurso"]
        if row["draw_index"]:
            rec["draw_index"] = row["draw_index"]
        rec.update(_deserialize_extra(row["extra_data"]))
        records.append(rec)
    return records


def get_lottery_status(
    lottery_key: str,
    *,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Metadados de cache por modalidade."""
    init_db(db_path)
    with _connect(db_path) as conn:
        meta = conn.execute(
            "SELECT last_update, last_concurso, total_records FROM lottery_metadata WHERE lottery_key = ?",
            (lottery_key,),
        ).fetchone()

    if meta is None:
        return {
            "lottery_key": lottery_key,
            "exists": False,
            "last_update": None,
            "last_concurso": None,
            "total_records": 0,
        }

    return {
        "lottery_key": lottery_key,
        "exists": int(meta["total_records"]) > 0,
        "last_update": meta["last_update"],
        "last_concurso": meta["last_concurso"],
        "total_records": int(meta["total_records"]),
    }


def get_all_lotteries_status(
    *,
    db_path: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Status de cache para todas as modalidades registradas no banco."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT lottery_key, last_update, last_concurso, total_records FROM lottery_metadata"
        ).fetchall()

    return {
        row["lottery_key"]: {
            "exists": int(row["total_records"]) > 0,
            "last_update": row["last_update"],
            "last_concurso": row["last_concurso"],
            "total_records": int(row["total_records"]),
        }
        for row in rows
    }


def import_from_xlsx_path(
    file_path: str,
    lottery_key: str,
    *,
    loader: Any,
    loader_kwargs: dict[str, Any],
    db_path: str | None = None,
) -> int:
    """Importa XLSX oficial para o banco via função loader existente."""
    df = loader(file_path, **loader_kwargs)
    records = df.to_dict(orient="records")
    return save_draws_full(lottery_key, records, db_path=db_path)


def atomic_replace_database(source_path: str, dest_path: str | None = None) -> None:
    """Copia banco de forma atômica (útil em backups)."""
    dest = dest_path or get_db_path()
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(suffix=".db", dir=Path(dest).parent)
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        tmp_path.write_bytes(Path(source_path).read_bytes())
        os.replace(tmp_path, dest)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
