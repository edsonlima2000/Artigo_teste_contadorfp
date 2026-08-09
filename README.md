# Automated Function Point Counter

Academic Python prototype for estimating Software Function Points from GitLab changes with Azure OpenAI support.

[Português](#português)

## Highlights

- GitLab branch, commit, merge-request, issue, and file analysis
- AI-assisted functional classification through Azure OpenAI
- Tkinter desktop interface
- A pytest suite with offline fakes for representative software-quality techniques

## Getting started

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ContadorSFP.py
```

Review the repository files before running commands that access external services or download models and datasets. Never commit credentials or personal data.

## Project status

This is an educational or experimental project. See [ROADMAP.md](ROADMAP.md) for intentionally scoped future work and [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes.

## License

Original source code is available under the [MIT License](LICENSE). Third-party datasets, models, media, services, course materials, and dependencies keep their own terms; see [THIRD_PARTY_NOTICE.md](THIRD_PARTY_NOTICE.md).

---

## Português

Protótipo acadêmico em Python para estimar Pontos de Função de Software a partir de alterações no GitLab, com classificação apoiada pelo Azure OpenAI. Inclui interface Tkinter e testes com fakes que não consomem serviços externos.

### Como começar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ContadorSFP.py
```

Consulte o [ROADMAP.md](ROADMAP.md) para funcionalidades futuras e o [CONTRIBUTING.md](CONTRIBUTING.md) antes de contribuir. Nunca envie credenciais ou dados pessoais ao repositório.

### Licença

O código-fonte original é disponibilizado sob a [Licença MIT](LICENSE). Datasets, modelos, mídias, serviços, materiais acadêmicos e dependências de terceiros preservam seus próprios termos; consulte [THIRD_PARTY_NOTICE.md](THIRD_PARTY_NOTICE.md).
