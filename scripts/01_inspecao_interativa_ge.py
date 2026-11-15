import os
import webbrowser
import pandas as pd

# ---------------------------------------------------------
# BLOCO 1: DEFINICAO DE ARQUIVOS E VOCABULARIOS CONTROLADOS
# ---------------------------------------------------------
ARQUIVO_ENTRADA = "../data/raw/ipes_ver2_com_Data(ipes_ver2).csv"
ARQUIVO_ATUALIZADO = "../data/raw/ipes_ver2_revisado.csv"

MAPA_ESPECIE = {
    "1": "amarelo",
    "2": "rosa",
    "3": "roxo",
    "4": "sucupira",
    "5": "margaridao",
    "0": "descartar",
}

MAPA_CONTEXTO = {
    "1": "pastagem",
    "2": "cerradao_savana",
    "3": "mata_galeria",
    "4": "borda_estrada",
    "0": "outro",
}

MAPA_CONFIANCA = {
    "1": "alta",
    "2": "media",
    "3": "baixa",
}

# ---------------------------------------------------------
# BLOCO 2: CARREGAMENTO COMPATIVEL COM EXCEL BRASIL (SEP=';' E LATIN1)
# ---------------------------------------------------------
def carregar_csv_seguro(caminho):
    try:
        df_temp = pd.read_csv(caminho, sep=";", encoding="latin1", dtype=str)
        if df_temp.shape[1] == 1:
            df_temp = pd.read_csv(caminho, sep=",", encoding="utf-8", dtype=str)
        return df_temp
    except UnicodeDecodeError:
        return pd.read_csv(caminho, sep=";", encoding="cp1252", dtype=str)

def executar_revisao():
    if os.path.exists(ARQUIVO_ATUALIZADO):
        df = carregar_csv_seguro(ARQUIVO_ATUALIZADO)
        print(f"Retomando a partir de '{ARQUIVO_ATUALIZADO}'.")
    else:
        df = carregar_csv_seguro(ARQUIVO_ENTRADA)
        print(f"Carregando base inicial '{ARQUIVO_ENTRADA}'.")

    for col, default in [
        ("data_imagem", df["Data"] if "Data" in df.columns else ""),
        ("especie_grupo", df["Name"] if "Name" in df.columns else ""),
        ("contexto", ""),
        ("confianca_visual", ""),
        ("observacoes", ""),
    ]:
        if col not in df.columns:
            df[col] = default

    colunas_texto = ["Data", "Name", "data_imagem", "especie_grupo", "contexto", "confianca_visual", "observacoes"]
    for col in colunas_texto:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip().replace({"nan": "", "NaN": "", "None": ""})

    pendentes = df[(df["data_imagem"] == "") | (df["contexto"] == "")].index.tolist()
    total_pendentes = len(pendentes)
    print(f"Total de registros: {len(df)} | Pendentes: {total_pendentes}")

    try:
        for n, idx in enumerate(pendentes, 1):
            row = df.loc[idx]
            obj_id = row["OBJECTID"]
            nome_original = row["Name"]
            lat = float(str(row["POINT_Y"]).replace(",", ".").strip())
            lon = float(str(row["POINT_X"]).replace(",", ".").strip())
            data_existente = row["data_imagem"]

            print(f"\n>>> PONTO [{n}/{total_pendentes}] | OBJECTID: {obj_id}")
            print(f"    Coordenadas: Lat {lat:.6f}, Lon {lon:.6f} | Classe Original: {nome_original}")

            ge_url = f"https://earth.google.com/web/@{lat},{lon},350a,350d,35y,0h,0t,0r"
            webbrowser.open_new_tab(ge_url)

            prompt_data = f"1. Data observada [{data_existente}]: " if data_existente else "1. Data observada (DD/MM/AAAA): "
            entrada_data = input(prompt_data).strip()

            if entrada_data.lower() == "sair":
                break
            if entrada_data.lower() == "pular":
                continue

            data_final = entrada_data if entrada_data else data_existente

            padrao_esp = "2" if "rosa" in nome_original.lower() else ("3" if "roxo" in nome_original.lower() else "1")
            print("2. Especie/Flor: [1] Amarelo | [2] Rosa | [3] Roxo | [4] Sucupira | [5] Margaridao | [0] Descartar")
            resp_esp = input(f"   Escolha [{padrao_esp}]: ").strip() or padrao_esp
            especie_final = MAPA_ESPECIE.get(resp_esp, nome_original)

            print("3. Contexto: [1] Pastagem | [2] Cerradao/Savana | [3] Mata de Galeria | [4] Borda/Estrada | [0] Outro")
            resp_ctx = input("   Escolha [1]: ").strip() or "1"
            contexto_final = MAPA_CONTEXTO.get(resp_ctx, "pastagem")

            print("4. Confianca Visual: [1] Alta | [2] Media | [3] Baixa")
            resp_conf = input("   Escolha [1]: ").strip() or "1"
            confianca_final = MAPA_CONFIANCA.get(resp_conf, "alta")

            obs = input("5. Observacoes (Enter para vazio): ").strip()

            df.at[idx, "data_imagem"] = str(data_final)
            df.at[idx, "especie_grupo"] = str(especie_final)
            df.at[idx, "contexto"] = str(contexto_final)
            df.at[idx, "confianca_visual"] = str(confianca_final)
            df.at[idx, "observacoes"] = str(obs)

            df.to_csv(ARQUIVO_ATUALIZADO, sep=";", encoding="latin1", index=False)
            print(f"OK - Ponto {obj_id} gravado.")

    except KeyboardInterrupt:
        print("\nExecucao interrompida via teclado.")
    finally:
        df.to_csv(ARQUIVO_ATUALIZADO, sep=";", encoding="latin1", index=False)

if __name__ == "__main__":
    executar_revisao()
