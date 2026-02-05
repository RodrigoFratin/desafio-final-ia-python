import json
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8080/v1", 
    api_key="sk-no-key-required"
)


def carregar_resenhas(caminho):
    """Etapa 1: Carrega o arquivo txt para uma lista."""
    with open(caminho, 'r', encoding='utf-8') as f:
        return [linha.strip() for linha in f if linha.strip()]

def processar_com_ia(lista_resenhas):
    """Etapa 2 e 3: Envia para a IA e transforma em Lista de Dicionários."""
    dados_finais = []
    
    for resenha in lista_resenhas:
        print(f"Processando: {resenha[:50]}...")
        
        prompt = f"""
        Analise a resenha abaixo e extraia as informações no formato JSON.
        Resenha: {resenha}
        
        O formato deve ser exatamente este:
        {{
            "usuario": "nome extraído",
            "resenha_original": "texto original",
            "resenha_traduzida": "tradução para português",
            "sentimento": "positivo, negativo ou neutro"
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="local-model", # O nome do modelo que você carregou no Llama
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            # Converte a string do modelo em um dicionário Python
            conteudo = response.choices[0].message.content
            # Garantindo que pegamos apenas o que está entre chaves {}
            json_puro = conteudo[conteudo.find("{"):conteudo.rfind("}")+1]
            dados_finais.append(json.loads(json_puro))
            
        except Exception as e:
            print(f"Erro ao processar resenha: {e}")
            
    return dados_finais

def gerar_analise_final(lista_dicts, separador=" | "):
    """Etapa 4: Conta sentimentos e concatena tudo em uma string."""
    contagem = {"positivo": 0, "negativo": 0, "neutro": 0}
    textos_unidos = []
    
    for item in lista_dicts:
        # Conta sentimentos
        sent = item.get('sentimento', '').lower()
        if sent in contagem:
            contagem[sent] += 1
            
        # Prepara a string (Usuário + Resenha Traduzida)
        texto = f"{item['usuario']}: {item['resenha_traduzida']}"
        textos_unidos.append(texto)
        
    resultado_string = separador.join(textos_unidos)
    return contagem, resultado_string

# --- EXECUÇÃO DO FLUXO ---
if __name__ == "__main__":
    # 1. Carregar
    resenhas_puras = carregar_resenhas("data/avaliacoes.txt")
    
    # 2 e 3. Processar (IA + JSON)
    lista_processada = processar_com_ia(resenhas_puras)
    
    # 4. Analisar
    contas, string_gigante = gerar_analise_final(lista_processada)
    
    print("\n--- RESULTADO FINAL ---")
    print(f"Sentimentos: {contas}")
    print(f"Conteúdo Consolidado: {string_gigante[:200]}...") # Mostra só o começo