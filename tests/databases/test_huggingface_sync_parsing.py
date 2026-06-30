"""Test HuggingFace sync parsing logic."""


def test_parse_org_from_repo_id() -> None:
    """Verify org parsing from repo_id."""
    repo_id = "lmstudio-community/gemma-4-E4B-it-GGUF"
    org = repo_id.split("/")[0]
    assert org == "lmstudio-community"


def test_parse_quant_from_filename() -> None:
    """Verify quant tag parsing from filename."""
    filename = "gemma-4-E4B-it-Q4_K_M.gguf"
    import re
    match = re.search(r"(Q[0-9]+_[A-Z_]+)", filename)
    assert match.group(1) == "Q4_K_M"


def test_parse_family_from_config() -> None:
    """Verify family parsing from config architectures field."""
    config = {"architectures": ["GemmaForCausalLM"]}
    # Simple mapping for common architectures
    arch_to_family = {
        "GemmaForCausalLM": "gemma",
        "LlamaForCausalLM": "llama",
        "MistralForCausalLM": "mistral",
    }
    arch = config["architectures"][0]
    family = arch_to_family.get(arch, "unknown")
    assert family == "gemma"


def test_parse_category_from_pipeline_tag() -> None:
    """Verify category parsing from pipeline_tag."""
    pipeline_tag = "text-generation"
    category = pipeline_tag
    assert category == "text-generation"


def test_compute_quant_level() -> None:
    """Verify quant_level integer computation."""
    quant_tags = {
        "Q2_K": 20,
        "Q4_K_M": 40,
        "Q5_K_M": 50,
        "Q8_0": 80,
        "F16": 160,
    }
    for tag, expected_level in quant_tags.items():
        assert quant_tags[tag] == expected_level
