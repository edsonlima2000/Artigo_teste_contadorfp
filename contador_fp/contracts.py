class ContractError(ValueError):
    """Erro de contrato funcional do SUT."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def validate_ai_response(response):
    require(isinstance(response, dict), "Resposta da IA deve ser um objeto JSON.")
    require("Total_SFP" in response, "Resposta da IA deve conter Total_SFP.")
    require("Elementos_FP" in response, "Resposta da IA deve conter Elementos_FP.")
    require(isinstance(response["Total_SFP"], (int, float)), "Total_SFP deve ser numerico.")
    require(isinstance(response["Elementos_FP"], list), "Elementos_FP deve ser uma lista.")
    require(response["Total_SFP"] >= 0, "Total_SFP nao pode ser negativo.")
    return response
