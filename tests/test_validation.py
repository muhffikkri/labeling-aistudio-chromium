# tests/test_validation.py
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core_logic.validation import parse_and_validate

def test_validation_success_perfect_input():
    raw_response = "POSITIF - Ini adalah sentimen positif.\nNEGATIF - Ini adalah sentimen negatif."
    is_valid, result = parse_and_validate(raw_response, expected_count=2)
    assert is_valid is True
    assert len(result) == 2
    assert result[0]["label"] == "POSITIF"
    assert result[1]["justification"] == "Ini adalah sentimen negatif."

def test_validation_fails_on_mismatched_count():
    raw_response = "POSITIF - Hanya satu baris."
    is_valid, result = parse_and_validate(raw_response, expected_count=2)
    assert is_valid is False
    assert "Jumlah baris output (1) tidak sesuai" in result

def test_validation_fails_on_invalid_label():
    raw_response = "POSITIF - OK\nBINGUNG - Label ini tidak ada."
    is_valid, result = parse_and_validate(raw_response, expected_count=2)
    assert is_valid is False
    assert "Ditemukan label tidak valid: BINGUNG" in result

def test_validation_handles_empty_input():
    is_valid, result = parse_and_validate("", expected_count=2)
    assert is_valid is False