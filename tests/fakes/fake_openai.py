class FakeAnalyzer:
    def __init__(self, response=None):
        self.response = response or {
            "Total_SFP": 3,
            "Elementos_FP": [
                {
                    "Nome_Arquivo": "app.py",
                    "Extensao": "py",
                    "Elemento_FP": "ALI",
                    "Pontos": 3,
                }
            ],
        }
        self.calls = []

    def consultar_especialista_ai(self, descricao_projeto, descricao_detalhada, caminho_arquivo):
        self.calls.append(
            {
                "descricao_projeto": descricao_projeto,
                "descricao_detalhada": descricao_detalhada,
                "caminho_arquivo": caminho_arquivo,
            }
        )
        return self.response
