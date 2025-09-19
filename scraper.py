import pandas as pd
import os
import random
from datetime import datetime, timedelta

def coletar_dados_financeiros():
    caminho_csv = 'dados.csv'

    # Se o arquivo não existir ou estiver vazio, cria dados históricos
    if not os.path.exists(caminho_csv) or os.path.getsize(caminho_csv) == 0:
        print("Gerando dados históricos para o primeiro uso...")
        data_inicial = datetime.now() - timedelta(days=7)
        datas = [data_inicial + timedelta(days=i) for i in range(7)]
        valores = [random.randint(2000, 3000) for _ in range(7)]
        
        df_novo = pd.DataFrame({
            'Data': datas,
            'Valor': valores,
            'Status': ['Estável'] * 7 # Status padrão
        })
        df_novo.to_csv(caminho_csv, index=False)
        print("Dados históricos criados com sucesso!")
        return

    # Se o arquivo já existir, adiciona um novo ponto de dados
    print("Adicionando novo ponto de dados...")
    df_existente = pd.read_csv(caminho_csv)

    ultimo_dia = pd.to_datetime(df_existente['Data'].iloc[-1])
    novo_dia = ultimo_dia + timedelta(days=1)
    
    # Simula um novo valor
    ultimo_valor = df_existente['Valor'].iloc[-1]
    novo_valor = ultimo_valor + random.randint(-150, 150)
    
    novo_status = 'Estável'
    if novo_valor > ultimo_valor:
        novo_status = 'Aumento'
    elif novo_valor < ultimo_valor:
        novo_status = 'Queda'
    
    df_novo = pd.DataFrame({
        'Data': [novo_dia],
        'Valor': [novo_valor],
        'Status': [novo_status]
    })
    
    df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    df_final.to_csv(caminho_csv, index=False)
    print("Novo ponto de dados adicionado com sucesso!")


if __name__ == '__main__':
    coletar_dados_financeiros()