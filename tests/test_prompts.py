"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt():
    data = load_prompts(PROMPT_PATH)
    return data["bug_to_user_story_v2"]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert prompt.get("system_prompt", "").strip()

    def test_prompt_has_role_definition(self, prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt["system_prompt"].lower()
        assert "product manager" in system_prompt

    def test_prompt_mentions_format(self, prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt["system_prompt"]
        assert "Markdown" in system_prompt
        assert "User Story" in system_prompt

    def test_prompt_has_few_shot_examples(self, prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt["system_prompt"]
        assert "### EXEMPLOS" in system_prompt
        assert system_prompt.count("Relato:") >= 2
        assert system_prompt.count("## User Story") >= 2

    def test_prompt_no_todos(self, prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full_text = prompt["system_prompt"] + prompt["user_prompt"]
        assert "TODO" not in full_text

    def test_minimum_techniques(self, prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        is_valid, errors = validate_prompt_structure(prompt)
        assert is_valid, errors
        assert len(prompt.get("techniques_applied", [])) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
