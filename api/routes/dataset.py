from fastapi import APIRouter, HTTPException

from api.services.core import load_dataset, update_dataset

router = APIRouter()

@router.get("/")
def get_dataset_info():
    """
    Retorna informações sobre o dataset
    """
    try:
        df = load_dataset()
        return {
            "total_records": len(df),
            "columns": list(df.columns),
            "last_update": "Verificar arquivo CSV para data de última atualização"
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dataset não encontrado. Use POST /dataset para criar/atualizar."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar dataset: {str(e)}")

@router.post("/")
def update_dataset_endpoint():
    """
    Atualiza o dataset baixando os dados mais recentes da Caixa Econômica Federal
    """
    try:
        df = update_dataset()
        return {
            "message": "Dataset atualizado com sucesso",
            "total_records": len(df),
            "columns": list(df.columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar dataset: {str(e)}")
