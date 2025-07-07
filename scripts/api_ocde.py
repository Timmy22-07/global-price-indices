import requests
import pandas as pd

def fetch_ocde_api(url: str) -> dict:
    """
    Télécharge et retourne le JSON brut depuis une API OCDE SDMX (version flat).
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erreur lors de la requête API OCDE : {e}")

def flatten_ocde_data(json_data: dict) -> pd.DataFrame:
    """
    Transforme le JSON SDMX 'flat' de l’OCDE en DataFrame pandas exploitable.
    """
    if "dataSets" not in json_data or not json_data["dataSets"]:
        raise ValueError("Pas de données disponibles dans la réponse JSON.")

    structure = json_data["structure"]["dimensions"]["observation"]
    series_data = json_data["dataSets"][0]["observations"]
    series_keys = list(series_data.keys())
    observations = []

    for key in series_keys:
        dim_indexes = list(map(int, key.split(":")))
        values = [structure[i]["values"][dim_indexes[i]]["id"] for i in range(len(dim_indexes))]
        obs_value = series_data[key][0]
        observations.append(values + [obs_value])

    columns = [dim["name"] for dim in structure] + ["Value"]
    df = pd.DataFrame(observations, columns=columns)

    return df
