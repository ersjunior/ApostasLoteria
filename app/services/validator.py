"""Reexporta validação de jogos do core de domínio."""

from loterias_core.validator import HIT_TIERS, analyze_game, check_game, count_hit_tiers

__all__ = ["HIT_TIERS", "analyze_game", "check_game", "count_hit_tiers"]
