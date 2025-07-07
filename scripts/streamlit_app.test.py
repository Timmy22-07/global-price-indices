from api_ocde import fetch_ocde_api, flatten_ocde_data

url = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PPP_M@DF_PP_CPL_M,/.M.FRA...?startPeriod=2025-05&dimensionAtObservation=AllDimensions"

json_data = fetch_ocde_api(url)
df = flatten_ocde_data(json_data)

print(df.head())