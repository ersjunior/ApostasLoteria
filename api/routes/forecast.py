from fastapi import APIRouter, HTTPException, Query

from api.services.core import load_dataset
from loterias_core.generator import generate_forecast_games

router = APIRouter()


@router.get("/")
def forecast(
    n: int = Query(default=10, ge=1, le=100, description="Número de jogos inéditos a gerar"),
):
    """
    Gera jogos da Mega-Sena que ainda não apareceram no histórico (combinações inéditas).
    """
    try:
        df = load_dataset()
        games = generate_forecast_games(df, n_games=n, total_bolas=6, universo=60)
        return {
            "n_games": n,
            "games": games,
            "message": "Jogos inéditos gerados com sucesso",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dataset não encontrado. Por favor, atualize o dataset primeiro (POST /dataset/).",
        ) from None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar jogos: {str(e)}") from e
