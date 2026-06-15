"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data["user_prompt"]),
        ])

        result = hub.push(
            prompt_name,
            prompt_template,
            new_repo_is_public=True,
        )

        print(f"Prompt publicado: {prompt_name}")
        print(f"Hub result: {result}")
        return True
    except Exception as exc:
        print(f"Erro no push para o LangSmith Hub: {exc}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = [
        "description",
        "system_prompt",
        "user_prompt",
        "version",
        "techniques_applied",
    ]

    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatorio faltando: {field}")

    system_prompt = str(prompt_data.get("system_prompt", "")).strip()
    user_prompt = str(prompt_data.get("user_prompt", "")).strip()

    if not system_prompt:
        errors.append("system_prompt esta vazio")

    if not user_prompt:
        errors.append("user_prompt esta vazio")

    full_text = f"{system_prompt}\n{user_prompt}"
    if "TODO" in full_text or "[TODO]" in full_text:
        errors.append("Prompt contem TODO pendente")

    techniques = prompt_data.get("techniques_applied", [])
    if not isinstance(techniques, list):
        errors.append("techniques_applied deve ser uma lista")
    elif len(techniques) < 2:
        errors.append(f"Minimo de 2 tecnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS")

    required_env = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_env):
        return 1

    yaml_path = "prompts/bug_to_user_story_v2.yml"
    data = load_yaml(yaml_path)
    if not data:
        print(f"Nao foi possivel carregar: {yaml_path}")
        return 1

    if "bug_to_user_story_v2" not in data:
        print("Chave 'bug_to_user_story_v2' nao encontrada no YAML")
        return 1

    prompt_data = data["bug_to_user_story_v2"]

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt invalido:")
        for error in errors:
            print(f" - {error}")
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_name = f"{username}/bug_to_user_story_v2"
    print(f"Publicando prompt: {prompt_name}")

    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    if not success:
        print("Falha ao publicar prompt")
        return 1

    print("Push concluido com sucesso")
    return 0


if __name__ == "__main__":
    sys.exit(main())
