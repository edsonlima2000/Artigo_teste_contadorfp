# Modelo do Dominio da Entrada

## Caracteristicas

| Caracteristica | Blocos |
| --- | --- |
| Projeto | existente; inexistente/inacessivel |
| Escopo | branch; merge request; branch com commit; nenhum escopo; branch e MR simultaneos |
| Arquivo | elegivel; inelegivel; inacessivel |
| Quantidade de arquivos elegiveis | zero; um; varios |
| Resposta da IA | JSON valido; JSON em markdown; JSON invalido; schema invalido |
| Tamanho da descricao | menor que bloco; igual ao limite; maior que limite |

## Valores limite

- Zero arquivos elegiveis.
- Exatamente um arquivo elegivel.
- Descricao exatamente no limite de `AZURE_OPENAI_TAMANHO_BLOCO`.
- `AZURE_OPENAI_MAX_RETRIES = 1`.
- Resposta com `Total_SFP = 0`.

## Cobertura implementada

- `tests/test_descriptions.py`
- `tests/test_fp_service.py`
- `tests/test_ai_client.py`
- `tests/test_acceptance.py`
