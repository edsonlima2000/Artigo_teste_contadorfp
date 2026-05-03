import logging
import os

import gitlab
import openai
from dotenv import load_dotenv


DEPLOYMENT_NAME = "StudioAI"
SUPPORTED_EXTENSIONS = [".py", ".jsp", ".jspx", ".js", ".ts", ".groovy", ".kt", ".scala"]


def setup_logging():
    logging.basicConfig(
        filename="execucao.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_environment():
    load_dotenv()


def configure_openai():
    openai.api_type = "azure"
    openai.api_version = "2024-02-01"
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")


def create_gitlab_client():
    return gitlab.Gitlab(
        os.getenv("GITLAB_ENDPOINT"),
        private_token=os.getenv("GITLAB_PRIVATE_TOKEN"),
    )


def bootstrap():
    print("Iniciando script...")
    setup_logging()
    load_environment()
    print("Variaveis de ambiente carregadas...")
    configure_openai()
    print("Azure OpenAI configurado...")
    client = create_gitlab_client()
    print("GitLab configurado...")
    return client
