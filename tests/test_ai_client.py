from types import SimpleNamespace

import pytest

from contador_fp.ai_client import AzureOpenAIAnalyzer
from contador_fp.contracts import ContractError


def make_response(content):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ]
    )


class FakeCompletions:
    def __init__(self, content):
        self.content = content

    def create(self, **kwargs):
        return make_response(self.content)


def test_ai_client_parses_json_response():
    analyzer = AzureOpenAIAnalyzer(FakeCompletions('{"Total_SFP": 2, "Elementos_FP": []}'))

    result = analyzer.consultar_especialista_ai("projeto", "detalhe", "app.py")

    assert result == {"Total_SFP": 2, "Elementos_FP": []}


def test_ai_client_parses_markdown_json_response():
    analyzer = AzureOpenAIAnalyzer(FakeCompletions('```json\n{"Total_SFP": 2, "Elementos_FP": []}\n```'))

    result = analyzer.consultar_especialista_ai("projeto", "detalhe", "app.py")

    assert result["Total_SFP"] == 2


def test_ai_client_rejects_invalid_schema():
    analyzer = AzureOpenAIAnalyzer(FakeCompletions('{"Total_SFP": "x", "Elementos_FP": []}'))

    with pytest.raises(ContractError):
        analyzer.consultar_especialista_ai("projeto", "detalhe", "app.py")
