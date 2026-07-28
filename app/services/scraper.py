from io import BytesIO

import pandas as pd
import requests

# URL estática conhecida (pode falhar no futuro)
STATIC_XLSX_URL = "https://loterias.caixa.gov.br/loterias/_arquivos/loterias/D_megasena.xlsx"


def download_megasena_data():
    """
    Tenta baixar o XLSX oficial da Mega-Sena.
    Se falhar, orienta uso de upload manual.
    """
    try:
        response = requests.get(STATIC_XLSX_URL, timeout=30)
        response.raise_for_status()

        df = pd.read_excel(BytesIO(response.content))

        if df.empty:
            raise RuntimeError("Arquivo XLSX vazio.")

        return df

    except Exception as e:
        raise RuntimeError(
            "Download automático indisponível.\n\n"
            "A Caixa não oferece uma API pública estável para este arquivo.\n"
            "➡️ Use o upload manual do XLSX oficial."
        ) from e
