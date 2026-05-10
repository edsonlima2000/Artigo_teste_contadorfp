class ContractError(ValueError):
    """Erro de contrato funcional do SUT."""


def require(condition, message):
    if not condition:
        raise ContractError(message)


def ensure(condition, message):
    if not condition:
        raise ContractError(message)


def invariant(condition, message):
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


def validate_fp_result(result):
    ensure(isinstance(result, dict), "Resultado da contagem deve ser um objeto.")
    ensure("Total_SFP" in result, "Resultado da contagem deve conter Total_SFP.")
    ensure("Elementos_FP" in result, "Resultado da contagem deve conter Elementos_FP.")
    ensure(isinstance(result["Total_SFP"], (int, float)), "Total_SFP final deve ser numerico.")
    ensure(isinstance(result["Elementos_FP"], list), "Elementos_FP final deve ser uma lista.")
    ensure(result["Total_SFP"] >= 0, "Total_SFP final nao pode ser negativo.")
    return result


def validate_processing_invariants(result):
    invariant(isinstance(result, dict), "Estado de processamento deve ser um objeto.")
    invariant("Total_SFP" in result, "Estado de processamento deve conter Total_SFP.")
    invariant("Elementos_FP" in result, "Estado de processamento deve conter Elementos_FP.")
    invariant(isinstance(result["Total_SFP"], (int, float)), "Total_SFP em processamento deve ser numerico.")
    invariant(isinstance(result["Elementos_FP"], list), "Elementos_FP em processamento deve ser uma lista.")
    invariant(result["Total_SFP"] >= 0, "Total_SFP em processamento nao pode ser negativo.")
    return result
