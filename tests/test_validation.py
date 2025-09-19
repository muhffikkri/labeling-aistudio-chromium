# tests/test_validation.py
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core_logic.validation import parse_and_validate

class TestParseAndValidate:
    """Test suite untuk fungsi parse_and_validate"""
    
    def setup_method(self):
        """Setup untuk setiap test method"""
        self.allowed_labels = ["POSITIF", "NEGATIF", "NETRAL", "TIDAK RELEVAN"]
    
    def test_valid_response_basic(self):
        """Test parsing response yang valid dengan format standar"""
        raw_response = """POSITIF - Komentar ini menunjukkan kepuasan terhadap produk
NEGATIF - Komentar ini mengkritik layanan yang buruk
NETRAL - Komentar ini hanya memberikan informasi faktual"""
        
        expected_count = 3
        is_valid, result = parse_and_validate(raw_response, expected_count, self.allowed_labels)
        
        assert is_valid == True
        assert len(result) == 3
        assert result[0]["label"] == "POSITIF"
        assert result[1]["label"] == "NEGATIF" 
        assert result[2]["label"] == "NETRAL"
        assert "kepuasan" in result[0]["justification"]
    
    def test_early_stopping_when_count_reached(self):
        """Test bahwa parsing berhenti setelah mencapai expected_count"""
        raw_response = """POSITIF - Bagus sekali
NEGATIF - Tidak suka
NETRAL - Biasa saja
POSITIF - Extra line yang seharusnya diabaikan
NEGATIF - Another extra line"""
        
        expected_count = 2
        is_valid, result = parse_and_validate(raw_response, expected_count, self.allowed_labels)
        
        assert is_valid == True
        assert len(result) == 2
        # Hanya 2 pertama yang diambil
        assert result[0]["label"] == "POSITIF"
        assert result[1]["label"] == "NEGATIF"
    
    def test_empty_response(self):
        """Test handling untuk response kosong"""
        is_valid, result = parse_and_validate("", 3, self.allowed_labels)
        assert is_valid == False
        assert "Tidak ada respons" in result
        
        is_valid, result = parse_and_validate(None, 3, self.allowed_labels)
        assert is_valid == False
        assert "Tidak ada respons" in result
    
    def test_cleanup_invalid_entries(self):
        """Test pembersihan entri yang tidak valid"""
        raw_response = """POSITIF - Justifikasi valid
NEGATIF - 
NETRAL - Justifikasi yang cukup panjang
POSITIF - ab
TIDAK RELEVAN - Justifikasi yang valid untuk completed"""
        
        expected_count = 3
        is_valid, result = parse_and_validate(raw_response, expected_count, self.allowed_labels)
        
        # Setelah pembersihan, hanya ada 3 valid (yang kedua dan keempat dibuang)
        assert is_valid == True
        assert len(result) == 3
        assert all(len(r["justification"]) >= 3 for r in result)
    
    def test_case_insensitive_labels(self):
        """Test bahwa parsing tidak case-sensitive"""
        raw_response = """positif - Label lowercase
NEGATIF - Label uppercase  
Netral - Label mixed case"""
        
        expected_count = 3
        is_valid, result = parse_and_validate(raw_response, expected_count, self.allowed_labels)
        
        assert is_valid == True
        assert result[0]["label"] == "POSITIF"  # Harus dinormalisasi ke uppercase
        assert result[1]["label"] == "NEGATIF"
        assert result[2]["label"] == "NETRAL"
    
    def test_count_mismatch(self):
        """Test handling ketika jumlah hasil tidak sesuai expected_count"""
        raw_response = """POSITIF - Hanya ada satu
NEGATIF - Dan satu lagi"""
        
        expected_count = 5  # Expect 5 tapi hanya ada 2
        is_valid, result = parse_and_validate(raw_response, expected_count, self.allowed_labels)
        
        assert is_valid == False
        assert "tidak sesuai dengan input" in result
    
    def test_empty_allowed_labels(self):
        """Test handling ketika allowed_labels kosong"""
        raw_response = "POSITIF - Test"
        
        is_valid, result = parse_and_validate(raw_response, 1, [])
        
        assert is_valid == False
        assert "Tidak ada label yang diizinkan" in result

# Legacy tests for backward compatibility
def test_validation_success_perfect_input():
    raw_response = "POSITIF - Ini adalah sentimen positif.\nNEGATIF - Ini adalah sentimen negatif."
    allowed_labels = ["POSITIF", "NEGATIF", "NETRAL", "TIDAK RELEVAN"]
    is_valid, result = parse_and_validate(raw_response, expected_count=2, allowed_labels=allowed_labels)
    assert is_valid is True
    assert len(result) == 2
    assert result[0]["label"] == "POSITIF"
    assert result[1]["justification"] == "Ini adalah sentimen negatif."

def test_validation_fails_on_mismatched_count():
    raw_response = "POSITIF - Hanya satu baris."
    allowed_labels = ["POSITIF", "NEGATIF", "NETRAL", "TIDAK RELEVAN"]
    is_valid, result = parse_and_validate(raw_response, expected_count=2, allowed_labels=allowed_labels)
    assert is_valid is False
    assert "tidak sesuai dengan input" in result

def test_validation_handles_empty_input():
    allowed_labels = ["POSITIF", "NEGATIF", "NETRAL", "TIDAK RELEVAN"]
    is_valid, result = parse_and_validate("", expected_count=2, allowed_labels=allowed_labels)
    assert is_valid is False