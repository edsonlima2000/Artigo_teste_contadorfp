import json
import os
import time

import openai

from .config import DEPLOYMENT_NAME
from .contracts import ContractError, require, validate_ai_response


class AzureOpenAIAnalyzer:
    def __init__(self, completion_client=None):
        self.completion_client = completion_client

    def consultar_especialista_ai(self, descricao_projeto, descricao_detalhada, caminho_arquivo):
        require(descricao_projeto, "descricao_projeto e obrigatoria.")
        require(descricao_detalhada, "descricao_detalhada e obrigatoria.")
        require(caminho_arquivo, "caminho_arquivo e obrigatorio.")
        require(os.path.exists("prompt.txt"), "prompt.txt deve existir na raiz do projeto.")

        tamanho_bloco = int(os.getenv("AZURE_OPENAI_TAMANHO_BLOCO", 12000))
        max_retries = int(os.getenv("AZURE_OPENAI_MAX_RETRIES", 5))
        retry_delay = int(os.getenv("AZURE_OPENAI_RETRY_DELAY", 10))
        require(tamanho_bloco > 0, "AZURE_OPENAI_TAMANHO_BLOCO deve ser maior que zero.")
        require(max_retries > 0, "AZURE_OPENAI_MAX_RETRIES deve ser maior que zero.")
        require(retry_delay >= 0, "AZURE_OPENAI_RETRY_DELAY nao pode ser negativo.")

        blocos = [
            descricao_detalhada[i : i + tamanho_bloco]
            for i in range(0, len(descricao_detalhada), tamanho_bloco)
        ]
        resultado_total = {"Total_SFP": 0, "Elementos_FP": []}

        for index, bloco in enumerate(blocos):
            print(f"Processando bloco {index + 1}/{len(blocos)} do arquivo {caminho_arquivo}...")

            with open("prompt.txt", "r", encoding="utf-8") as file:
                prompt_template = file.read()

            prompt = prompt_template.replace("{{descricao_projeto}}", descricao_projeto).replace(
                "{{descricao_detalhada}}", bloco
            )
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"{descricao_projeto}\n\n{bloco}\nArquivo: {caminho_arquivo}"},
            ]

            for _ in range(max_retries):
                try:
                    completion_client = self.completion_client or openai.chat.completions
                    response = completion_client.create(
                        model=DEPLOYMENT_NAME,
                        messages=messages,
                        max_tokens=3000,
                        temperature=0.2,
                        top_p=1.0,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                    )

                    content = response.choices[0].message.content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]

                    resposta = validate_ai_response(json.loads(content))
                    resultado_total["Total_SFP"] += resposta.get("Total_SFP", 0)
                    resultado_total["Elementos_FP"].extend(resposta.get("Elementos_FP", []))
                    break

                except openai.OpenAIError as error:
                    print(f"Erro da API ao acessar o assistente AI para o bloco {index + 1}: {error}")
                    time.sleep(retry_delay)
                except json.JSONDecodeError:
                    print("Erro ao decodificar a resposta da API.")
                    break
                except ContractError:
                    raise
                except Exception as error:
                    print(f"Erro inesperado ao acessar o assistente AI para o bloco {index + 1}: {error}")
                    break

        return resultado_total
