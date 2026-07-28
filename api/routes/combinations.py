from fastapi import APIRouter, HTTPException, Query

from api.services.core import load_dataset
from loterias_core.generator import generate_unique_combinations

router = APIRouter()


@router.get("/")
def generate_combinations(
    n: int = Query(default=10, ge=1, le=100, description="Número de combinações inéditas a gerar"),
):
    """
    Gera combinações inéditas da Mega-Sena por sorteio aleatório (sem modelo preditivo).
    """
    try:
        df = load_dataset()
        games = generate_unique_combinations(df, n_games=n, total_bolas=6, universo=60)
        return {
            "n_games": n,
            "games": games,
            "message": "Combinações inéditas geradas com sucesso",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dataset não encontrado. Por favor, atualize o dataset primeiro (POST /dataset/).",
        ) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar combinações: {str(e)}") from e
