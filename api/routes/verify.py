from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.core import load_dataset
from app.services.validator import check_game

router = APIRouter()

class Game(BaseModel):
    numbers: list[int]

@router.post("/")
def verify(game: Game):
    """
    Verifica se um jogo da Mega-Sena já foi sorteado
    """
    if len(game.numbers) != 6:
        raise HTTPException(status_code=400, detail="Um jogo da Mega-Sena deve ter exatamente 6 números")
    
    if not all(1 <= n <= 60 for n in game.numbers):
        raise HTTPException(status_code=400, detail="Os números devem estar entre 1 e 60")
    
    try:
        df = load_dataset()
        found = check_game(sorted(game.numbers), df)
        
        return {
            "numbers": sorted(game.numbers),
            "found": found,
            "message": "Jogo já foi sorteado" if found else "Jogo nunca foi sorteado"
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dataset não encontrado. Por favor, atualize o dataset primeiro."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar jogo: {str(e)}")
