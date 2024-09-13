import os
from dotenv import load_dotenv
import openai

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Acessar as variáveis de ambiente
api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

# Definir a chave da API
openai.api_key = api_key

# Definir o endpoint do Azure OpenAI diretamente
openai.azure_endpoint = azure_endpoint

# Nome do deployment para o gpt-4o
deployment_name = 'StudioAI'  # Substitua pelo nome do deployment correto no Azure

# Definir a frase inicial (start phrase)
start_phrase = 'Write a tagline for an ice cream shop.'

# Definir a versão da API
openai.api_version = "2024-02-01"  # Substitua pela versão correta da API

# Ajustar o nome do deployment para 'StudioAI' se este for o nome correto
deployment_name = 'StudioAI'

# Enviar uma solicitação de conclusão usando o modelo gpt-4o
completion = openai.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user", 
            "content": start_phrase,
        },
    ],
)

# Exibir a resposta
print(start_phrase + completion.choices[0].message.content)