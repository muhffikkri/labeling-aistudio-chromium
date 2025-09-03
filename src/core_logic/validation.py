import logging
import re
from typing import List, Tuple, Dict, Any

# Definisikan label yang valid di satu tempat agar mudah diubah jika perlu.
ALLOWED_LABELS = {"POSITIF", "NEGATIF", "NETRAL", "TIDAK RELEVAN"}

def parse_and_validate(raw_response: str | None, expected_count: int) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Mem-parsing respons mentah, memvalidasi format, label, dan jumlah baris.

    Fungsi ini melakukan tiga pengecekan utama:
    1.  **Jumlah Baris**: Jumlah hasil yang diparsing harus sama dengan jumlah item yang dikirim.
    2.  **Kesesuaian Label**: Setiap label harus merupakan salah satu dari `ALLOWED_LABELS`.
    3.  **Format Output**: Setiap baris harus mengikuti format yang diharapkan (misal: "LABEL - JUSTIFIKASI").

    Args:
        raw_response (str | None): Teks respons mentah dari model AI.
        expected_count (int): Jumlah baris yang diharapkan dalam respons.

    Returns:
        Tuple[bool, Union[List[Dict], str]]: 
        - (True, [data_terstruktur]) jika valid.
        - (False, "pesan_error") jika tidak valid.
    """
    # Kasus 1: Tidak ada respons sama sekali.
    if not raw_response:
        return False, "Validasi Gagal: Tidak ada respons yang diterima dari model."

    parsed_results = []
    lines = raw_response.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue  # Lewati baris kosong

        # Coba parsing dengan format utama: "LABEL - Justifikasi"
        parts = line.split(' - ', 1)
        if len(parts) == 2:
            label = parts[0].strip().upper()
            justification = parts[1].strip()
            parsed_results.append((label, justification))
            continue

        # (Opsional) Tambahkan logika parsing alternatif di sini jika diperlukan
        # Contoh: "1. LABEL: Justifikasi"
        match = re.search(r'^\d+\.\s*(\w+)\s*:\s*(.+)$', line)
        if match:
            label = match.group(1).strip().upper()
            justification = match.group(2).strip()
            parsed_results.append((label, justification))
            continue
        
        # Jika tidak ada format yang cocok, catat sebagai baris yang tidak dapat diparsing.
        logging.warning(f"Baris tidak dapat diparsing dan akan dilewati: '{line}'")

    # Kasus 2: Jumlah baris yang berhasil diparsing tidak cocok dengan yang diharapkan.
    if len(parsed_results) != expected_count:
        error_msg = f"Validasi Gagal: Jumlah baris output ({len(parsed_results)}) tidak sesuai dengan input ({expected_count})."
        logging.warning(error_msg)
        return False, error_msg

    # Kasus 3: Periksa apakah ada label yang tidak valid.
    invalid_labels_found = []
    for label, justification in parsed_results:
        if label not in ALLOWED_LABELS:
            invalid_labels_found.append(label)

    if invalid_labels_found:
        # Mengambil hanya label unik yang salah untuk pesan error yang lebih bersih
        unique_invalid_labels = list(set(invalid_labels_found))
        error_msg = f"Validasi Gagal: Ditemukan label tidak valid: {', '.join(unique_invalid_labels)}."
        logging.warning(error_msg)
        return False, error_msg

    # Jika semua validasi lolos, format data ke dalam struktur yang bersih.
    structured_results = [{"label": r[0], "justification": r[1]} for r in parsed_results]
    logging.info(f"Validasi berhasil untuk {len(structured_results)} baris.")
    
    return True, structured_results