import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os
import datetime
import time
from flask import Flask, render_template, request, send_file

# Configuração do Flask
app = Flask(__name__)

# Função para gerar dados reais da bolsa de valores
def gerar_dados_reais(ticker_simbolo):
    """Gera e retorna dados reais de ações do Yahoo Finance."""
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            print(f"Tentativa {tentativa + 1} de {max_tentativas} para baixar dados de {ticker_simbolo}...")
            # Pega os dados dos últimos 30 dias
            dados_yf = yf.download(ticker_simbolo, period='1mo')
            
            if not dados_yf.empty:
                print("Dados baixados com sucesso.")
                
                # Cria um DataFrame com os dados de fechamento, verificando ambas as colunas
                if 'Close' in dados_yf.columns:
                    data = pd.DataFrame(dados_yf['Close'])
                elif 'Adj Close' in dados_yf.columns:
                    data = pd.DataFrame(dados_yf['Adj Close'])
                else:
                    raise KeyError("Nenhuma coluna 'Close' ou 'Adj Close' encontrada.")

                # Converte a data (índice) para uma coluna e renomeia
                data = data.rename(columns={data.columns[0]: 'VALOR'})
                data = data.reset_index()
                data = data.rename(columns={'Date': 'DATA'})

                # Analisa a tendência somente se houver dados suficientes
                analise_texto = "Análise de tendência disponível após 10 entradas de dados."
                tendencia_atual = "Aguardando dados"
                
                if len(data) >= 10:
                    ultimos_valores = data['VALOR'].tail(5)
                    media_ultimos = ultimos_valores.mean()
                    media_anteriores = data['VALOR'].iloc[-10:-5].mean()
                    
                    if media_ultimos > media_anteriores * 1.05:
                        tendencia_atual = "Forte Alta"
                        analise_texto = "A tendência de valor é de **forte alta** nos últimos dias. O mercado está aquecido e a recomendação é de aproveitar o momento."
                    elif media_ultimos > media_anteriores * 1.01:
                        tendencia_atual = "Leve Alta"
                        analise_texto = "A tendência de valor é de **leve alta** nos últimos dias. Aumentos graduais podem sinalizar um mercado em crescimento."
                    elif media_ultimos < media_anteriores * 0.95:
                        tendencia_atual = "Forte Queda"
                        analise_texto = "A tendência de valor é de **forte queda** nos últimos dias. Recomenda-se **cautela** e análise aprofundada."
                    elif media_ultimos < media_anteriores * 0.99:
                        tendencia_atual = "Leve Queda"
                        analise_texto = "A tendência de valor é de **leve queda** nos últimos dias. Mantenha-se atento às oscilações e evite decisões precipitadas."
                    else:
                        tendencia_atual = "Estável"
                        analise_texto = "A tendência de valor está **estável** nos últimos dias. Não há grandes variações, indicando um mercado sem grandes emoções."
                        
                return data, analise_texto, tendencia_atual
            
            else:
                print("Dados vazios recebidos. Tentando novamente...")
                time.sleep(10) # Espera 10 segundos antes de tentar novamente
        
        except Exception as e:
            print(f"Ocorreu um erro na tentativa {tentativa + 1}: {e}")
            if tentativa < max_tentativas - 1:
                print("Tentando novamente em 10 segundos...")
                time.sleep(10)
    
    # Se todas as tentativas falharem
    return pd.DataFrame(columns=['DATA', 'VALOR']), "Erro: Não foi possível carregar dados. Verifique sua conexão com a internet ou o símbolo da ação.", "Erro"


# Função para gerar o gráfico
def gerar_grafico(data):
    """Gera e salva o gráfico da tendência dos dados."""
    if data.empty or 'DATA' not in data.columns or 'VALOR' not in data.columns:
        print("Dados incompletos. Não é possível gerar o gráfico.")
        return
        
    IMAGES_DIR = 'static/images'
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    plt.figure(figsize=(10, 6), facecolor='#3b3e5a')
    ax = plt.gca()
    ax.set_facecolor('#3b3e5a')
    
    plt.plot(pd.to_datetime(data['DATA']).dt.strftime('%d-%m'), data['VALOR'], marker='o', color='#a0a6eb', linewidth=2)
    
    plt.title('Tendência de Valor ao Longo do Tempo', color='#f0f4f8')
    plt.xlabel('Data', color='#c9d2db')
    plt.ylabel('Valor', color='#c9d2db')
    
    plt.tick_params(axis='x', colors='#c9d2db', rotation=45)
    plt.tick_params(axis='y', colors='#c9d2db')
    
    plt.grid(True, linestyle='--', alpha=0.3, color='#c9d2db')
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, 'tendencia.png'))
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    """Rota principal para exibir o dashboard."""
    ticker = 'PETR4.SA' # Ticker padrão
    if request.method == 'POST':
        ticker = request.form['ticker_input']

    dados, analise_texto, tendencia = gerar_dados_reais(ticker)
    
    gerar_grafico(dados)
    
    if not dados.empty:
        tabela_html = dados.to_html(classes=['table'], justify='left', index=False)
    else:
        tabela_html = ""
        
    return render_template('index.html', tabela=tabela_html, analise=analise_texto, tendencia=tendencia, ticker_atual=ticker)

@app.route('/atualizar_dados', methods=['POST'])
def atualizar_dados():
    """Rota para atualizar os dados e a página."""
    ticker = request.form['ticker_input']
        
    dados, analise_texto, tendencia = gerar_dados_reais(ticker)
    
    gerar_grafico(dados)
    
    if not dados.empty:
        tabela_html = dados.to_html(classes=['table'], justify='left', index=False)
    else:
        tabela_html = ""
        
    return render_template('index.html', tabela=tabela_html, analise=analise_texto, tendencia=tendencia, ticker_atual=ticker)

@app.route('/salvar_dados', methods=['POST'])
def salvar_dados():
    """Rota para salvar os dados em um arquivo CSV e enviá-lo ao usuário."""
    ticker = request.form['ticker_input']
    dados, _, _ = gerar_dados_reais(ticker)
    
    if not dados.empty:
        # Cria um nome de arquivo único com a data e o ticker
        data_atual = datetime.datetime.now().strftime("%Y-%m-%d")
        caminho_arquivo = os.path.join('downloads', f'{ticker}_{data_atual}.csv')
        
        # Cria o diretório de downloads se ele não existir
        os.makedirs('downloads', exist_ok=True)
        
        # Salva o DataFrame no arquivo CSV
        dados.to_csv(caminho_arquivo, index=False)
        
        # Envia o arquivo ao navegador
        return send_file(caminho_arquivo, as_attachment=True, download_name=f'{ticker}_{data_atual}.csv')
    
    return "Erro ao salvar dados. Verifique o ticker e tente novamente.", 400

if __name__ == '__main__':
    app.run(debug=True)
