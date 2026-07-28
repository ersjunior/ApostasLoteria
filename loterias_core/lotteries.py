"""Definições declarativas das modalidades de loteria."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LotteryConfig:
    """Configuração declarativa de uma modalidade de loteria."""

    name: str
    key: str
    icon: str
    color: str
    total_bolas: int
    universo: int
    placeholder: str
    file_path: str
    price_table: dict[int, float]
    multiple_draws: bool = False
    special_handler: str | None = None
    extra_fields: dict[str, int] | None = None
    portal_modalidade: str = ""

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "key": self.key,
            "icon": self.icon,
            "color": self.color,
            "total_bolas": self.total_bolas,
            "universo": self.universo,
            "placeholder": self.placeholder,
            "file_path": self.file_path,
            "price_table": self.price_table,
            "portal_modalidade": self.portal_modalidade,
        }
        if self.multiple_draws:
            data["multiple_draws"] = True
        if self.special_handler:
            data["special_handler"] = self.special_handler
        if self.extra_fields:
            data["extra_fields"] = self.extra_fields
        return data


LOTTERY_CONFIGS: tuple[LotteryConfig, ...] = (
    LotteryConfig(
        name="Mega-Sena",
        key="megasena",
        icon="🎰",
        color="#2563eb",
        total_bolas=6,
        universo=60,
        placeholder="01, 05, 12, 23, 34, 56",
        file_path="app/data/Mega-Sena.xlsx",
        portal_modalidade="Mega-Sena",
        price_table={
            6: 6.00,
            7: 42.00,
            8: 168.00,
            9: 504.00,
            10: 1260.00,
            11: 2772.00,
            12: 5544.00,
            13: 10296.00,
            14: 18018.00,
            15: 30030.00,
            16: 48048.00,
            17: 74256.00,
            18: 111384.00,
            19: 162792.00,
            20: 232560.00,
        },
    ),
    LotteryConfig(
        name="Lotofácil",
        key="lotofacil",
        icon="🍀",
        color="#16a34a",
        total_bolas=15,
        universo=25,
        placeholder="1, 2, 3, ..., 15",
        file_path="app/data/Lotofácil.xlsx",
        portal_modalidade="Lotofacil",
        price_table={
            15: 3.00,
            16: 48.00,
            17: 408.00,
            18: 2448.00,
            19: 11628.00,
            20: 46512.00,
        },
    ),
    LotteryConfig(
        name="Quina",
        key="quina",
        icon="🎯",
        color="#9333ea",
        total_bolas=5,
        universo=80,
        placeholder="01, 02, 03, 04, 05",
        file_path="app/data/Quina.xlsx",
        portal_modalidade="Quina",
        price_table={
            5: 2.50,
            6: 15.00,
            7: 52.50,
            8: 140.00,
            9: 315.00,
            10: 630.00,
            11: 1155.00,
            12: 1980.00,
            13: 3217.50,
            14: 5005.00,
            15: 7507.50,
        },
    ),
    LotteryConfig(
        name="Dupla Sena",
        key="duplasena",
        icon="🔁",
        color="#0ea5e9",
        total_bolas=6,
        universo=50,
        placeholder="01, 02, 03, 04, 05, 06",
        file_path="app/data/Dupla Sena.xlsx",
        portal_modalidade="Dupla Sena",
        multiple_draws=True,
        price_table={
            6: 2.50,
            7: 17.50,
            8: 70.00,
            9: 210.00,
            10: 525.00,
            11: 1155.00,
            12: 2310.00,
            13: 4290.00,
            14: 7507.50,
            15: 12512.50,
        },
    ),
    LotteryConfig(
        name="Lotomania",
        key="lotomania",
        icon="🎲",
        color="#f97316",
        total_bolas=50,
        universo=100,
        placeholder="50 dezenas (01–100)",
        file_path="app/data/Lotomania.xlsx",
        portal_modalidade="Lotomania",
        special_handler="lotomania",
        price_table={50: 3.00},
    ),
    LotteryConfig(
        name="Dia de Sorte",
        key="diadesorte",
        icon="🌞",
        color="#eab308",
        total_bolas=7,
        universo=31,
        placeholder="01, 02, 03, 04, 05, 06, 07",
        file_path="app/data/Dia de Sorte.xlsx",
        portal_modalidade="Dia de Sorte",
        price_table={
            7: 2.50,
            8: 20.00,
            9: 90.00,
            10: 300.00,
            11: 825.00,
            12: 1980.00,
            13: 4290.00,
            14: 8580.00,
            15: 16087.50,
        },
    ),
    LotteryConfig(
        name="Timemania",
        key="timemania",
        icon="⚽",
        color="#22c55e",
        total_bolas=7,
        universo=80,
        placeholder="7 dezenas + Time do Coração",
        file_path="app/data/Timemania.xlsx",
        portal_modalidade="Timemania",
        extra_fields={"timecoração": 1},
        price_table={7: 3.50},
    ),
    LotteryConfig(
        name="Super Sete",
        key="supersete",
        icon="7️⃣",
        color="#ef4444",
        total_bolas=7,
        universo=10,
        placeholder="7 números (0–9)",
        file_path="app/data/Super Sete.xlsx",
        portal_modalidade="Super Sete",
        special_handler="supersete",
        price_table={
            7: 2.50,
            8: 20.00,
            9: 90.00,
            10: 300.00,
            11: 825.00,
            12: 1980.00,
            13: 4290.00,
            14: 8580.00,
            15: 16087.50,
        },
    ),
    LotteryConfig(
        name="+Milionária",
        key="mais_milionaria",
        icon="💎",
        color="#7c3aed",
        total_bolas=6,
        universo=50,
        placeholder="6 dezenas + 2 trevos",
        file_path="app/data/+Milionária.xlsx",
        portal_modalidade="+Milionaria",
        special_handler="mais_milionaria",
        price_table={6: 6.00},
    ),
)

LOTTERIES: dict[str, dict[str, Any]] = {
    cfg.name: cfg.to_dict() for cfg in LOTTERY_CONFIGS
}

# Índice auxiliar por chave interna (ex: "megasena")
LOTTERIES_BY_KEY: dict[str, LotteryConfig] = {cfg.key: cfg for cfg in LOTTERY_CONFIGS}
