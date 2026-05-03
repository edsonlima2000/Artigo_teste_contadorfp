# Maquina de Estados do Processamento

## Estados

1. Inicio
2. Ambiente configurado
3. Projeto selecionado
4. Escopo definido
5. Artefatos recuperados
6. Arquivos filtrados
7. Analise em processamento
8. Resultado gerado
9. Erro de entrada
10. Erro de integracao

## Transicoes principais

| Origem | Guarda | Acao | Destino |
| --- | --- | --- | --- |
| Inicio | variaveis carregadas | criar clientes | Ambiente configurado |
| Ambiente configurado | projeto valido | carregar issues/branches/MRs | Projeto selecionado |
| Projeto selecionado | escopo valido | fixar referencia SHA | Escopo definido |
| Escopo definido | GitLab retorna arvore/diff | recuperar artefatos | Artefatos recuperados |
| Artefatos recuperados | extensao suportada | filtrar arquivos | Arquivos filtrados |
| Arquivos filtrados | arquivos elegiveis > 0 | chamar IA | Analise em processamento |
| Analise em processamento | JSON valido | agregar Total_SFP | Resultado gerado |
| Projeto selecionado | escopo ausente/ambiguo | exibir erro | Erro de entrada |
| Escopo definido | falha GitLab nao recuperavel | registrar erro | Erro de integracao |

## Evidencia automatizada

- Caminho feliz por branch: `tests/test_acceptance.py`
- Caminho com arquivos inelegiveis: `tests/test_acceptance.py`
- Caminho por commit: `tests/test_fp_service.py`
- Contrato da resposta da IA: `tests/test_ai_client.py`
