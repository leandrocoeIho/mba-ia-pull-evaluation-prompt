"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 no Hub e salva em YAML local."""
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = Path("prompts/bug_to_user_story_v1.yml")

    try:
        print(f"Fazendo pull do prompt: {prompt_name}")
        prompt = hub.pull(prompt_name)
    except Exception as exc:
        print(f"Erro ao fazer pull do prompt no Hub: {exc}")
        return False

    try:
        messages = getattr(prompt, "messages", [])
        if len(messages) < 2:
            print("Formato de prompt inesperado: mensagens insuficientes.")
            return False

        system_prompt = messages[0].prompt.template
        user_prompt = messages[1].prompt.template

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        saved = save_yaml(prompt_data, str(output_path))
        if not saved:
            print(f"Falha ao salvar arquivo local: {output_path}")
            return False

        print(f"Prompt salvo com sucesso em: {output_path}")
        return True
    except Exception as exc:
        print(f"Erro ao processar prompt recebido: {exc}")
        return False


def main():
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        print("Variaveis de ambiente necessarias nao estao definidas. Verifique o .env.")
        return 1

    ok = pull_prompts_from_langsmith()
    if not ok:
        print("Falha ao trazer prompt do LangSmith Hub.")
        return 1

    print("Pull concluido com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
