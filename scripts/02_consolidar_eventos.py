import pandas as pd

# ---------------------------------------------------------
# BLOCO 1: CARREGAMENTO DA TABELA REVISADA
# ---------------------------------------------------------
ARQUIVO_REVISADO = "../data/raw/ipes_ver2_revisado.csv"
ARQUIVO_SAIDA = "../data/processed/ipes_eventos_consolidados.csv"

df = pd.read_csv(ARQUIVO_REVISADO, sep=";", encoding="latin1", dtype=str)

for col in df.columns:
    df[col] = df[col].fillna("").astype(str).str.strip().replace({"nan": "", "NaN": "", "None": ""})

# ---------------------------------------------------------
# BLOCO 2: CORRECOES PONTUAIS E FILTRO DE DESCARTE
# ---------------------------------------------------------
df.loc[df["OBJECTID"] == "403", "data_imagem"] = "17/06/2024"
df.loc[df["OBJECTID"] == "438", "data_imagem"] = "24/07/2021"
df.loc[df["OBJECTID"].isin(["226", "227", "228"]), "especie_grupo"] = "descartar"

df_validos = df[df["especie_grupo"] != "descartar"].copy()

# ---------------------------------------------------------
# BLOCO 3: PADRONIZACAO DE DATAS (ISO 8601: AAAA-MM-DD)
# ---------------------------------------------------------
MESES_PT = {
    "jan": "01", "fev": "02", "mar": "03", "abr": "04",
    "mai": "05", "jun": "06", "jul": "07", "ago": "08",
    "set": "09", "out": "10", "nov": "11", "dez": "12"
}

def padronizar_data(data_str):
    data_str = str(data_str).strip().lower()
    if not data_str or data_str in ["nan", "none"]:
        return ""
    partes = data_str.split("/")
    if len(partes) != 3:
        return data_str
    dia, mes, ano = partes[0].zfill(2), partes[1], partes[2]
    mes = MESES_PT[mes] if mes in MESES_PT else mes.zfill(2)
    if len(ano) == 2:
        ano = "20" + ano
    return f"{ano}-{mes}-{dia}"

df_validos["data_evento_1"] = df_validos["data_imagem"].apply(padronizar_data)
df_validos["data_original_iso"] = df_validos["Data"].apply(padronizar_data)

# ---------------------------------------------------------
# BLOCO 4: DESDOBRAMENTO POR EVENTO (PONTO + DATA)
# ---------------------------------------------------------
linhas_eventos = []

for _, row in df_validos.iterrows():
    obj_id = int(row["OBJECTID"])
    lat = float(row["POINT_Y"].replace(",", "."))
    lon = float(row["POINT_X"].replace(",", "."))
    obs = row["observacoes"]
    obs_lower = obs.lower()

    oip_presente = "oip" in obs_lower or "individuo" in obs_lower
    oip_multicor = any(k in obs_lower for k in ["incluindo", "outro amarelo"])
    area_interesse = "interesse" in obs_lower

    datas = [row["data_evento_1"]]
    if row["data_original_iso"] and row["data_original_iso"] != row["data_evento_1"]:
        datas.append(row["data_original_iso"])
    if obj_id == 460 and "2024-06-17" not in datas:
        datas.append("2024-06-17")

    for seq, dt in enumerate(datas, 1):
        conf = "media" if (obj_id == 460 and seq == 2) else row["confianca_visual"]
        linhas_eventos.append({
            "evento_id": f"{obj_id}_{seq}",
            "individuo_id": obj_id,
            "lat": round(lat, 7),
            "lon": round(lon, 7),
            "data_evento": dt,
            "ano": int(dt.split("-")[0]) if "-" in dt else None,
            "mes": int(dt.split("-")[1]) if "-" in dt else None,
            "classe_flor": row["especie_grupo"],
            "contexto": row["contexto"],
            "confianca": conf,
            "oip_presente": oip_presente,
            "oip_multicor": oip_multicor,
            "area_interesse": area_interesse,
            "observacoes_originais": obs
        })

df_final = pd.DataFrame(linhas_eventos)
df_final.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")
print(f"Consolidacao concluida: {len(df_final)} eventos gerados em '{ARQUIVO_SAIDA}'.")
