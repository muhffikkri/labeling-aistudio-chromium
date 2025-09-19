import logging
import re
from typing import List, Tuple, Dict, Any

def parse_and_validate(
    raw_response: str | None,
    expected_count: int,
    allowed_labels: List[str]
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Mem-parsing respons mentah dengan logika ketat dan daftar label yang dapat disesuaikan.

    Args:
        raw_response (str | None): Teks respons mentah dari model AI.
        expected_count (int): Jumlah baris yang diharapkan dalam respons.
        allowed_labels (List[str]): Daftar string label yang valid (misal: ["POSITIF", "NEGATIF"]).
    """
    if not raw_response:
        return False, "Validasi Gagal: Tidak ada respons yang diterima dari model."
        
    if not allowed_labels:
        return False, "Validasi Gagal: Tidak ada label yang diizinkan yang diberikan untuk validasi."

    # Log raw response untuk tracking
    logging.info(f"Raw response yang akan di-parse (panjang: {len(raw_response)} karakter)")
    
    # Buat set untuk pencocokan yang lebih cepat dan ubah ke huruf besar
    allowed_labels_set = {label.upper() for label in allowed_labels}
    
    parsed_results = []
    lines = raw_response.strip().split('\n')
    
    # Log total baris yang akan diproses
    logging.info(f"Total baris dalam raw response: {len(lines)}, Expected: {expected_count}")

    # Buat Regex secara dinamis dari daftar label yang diizinkan
    # re.escape() digunakan untuk menangani label yang mungkin memiliki karakter khusus
    label_pattern = "|".join(re.escape(label) for label in allowed_labels_set)
    valid_line_regex = re.compile(rf"^({label_pattern})\s*-\s*.+", re.IGNORECASE)

    for line_num, line in enumerate(lines, 1):
        # HENTIKAN PARSING JIKA SUDAH MENCAPAI JUMLAH YANG DIMINTA
        if len(parsed_results) >= expected_count:
            logging.info(f"✓ Telah mengumpulkan {expected_count} baris valid. Menghentikan parsing pada baris ke-{line_num}.")
            logging.info(f"Sisa {len(lines) - line_num + 1} baris diabaikan.")
            break

        line = line.strip()
        if not line:
            continue

        # Log setiap baris yang sedang diproses
        logging.debug(f"Memproses baris {line_num}: '{line[:100]}{'...' if len(line) > 100 else ''}'")
        
        # Cek apakah baris mengandung tag HTML
        html_tags = re.findall(r'<.*?>', line)
        if html_tags:
            logging.info(f"Baris {line_num} mengandung tag HTML: {html_tags}")

        if valid_line_regex.match(line):
            try:
                parts = line.split(' - ', 1)
                label = parts[0].strip().upper()
                # Pengecekan kedua untuk memastikan label ada di set kita
                if label in allowed_labels_set:
                    justification = parts[1].strip()
                    parsed_results.append((label, justification))
                    logging.debug(f"✓ Baris {line_num} berhasil di-parse: {label}")
                else:
                    # Seharusnya jarang terjadi karena regex, tapi sebagai pengaman
                    logging.warning(f"Mengabaikan baris {line_num} karena label '{label}' tidak ada di daftar yang diizinkan.")
            except IndexError:
                logging.warning(f"Mengabaikan baris {line_num} karena format tidak valid (tidak ada ' - ').")
                continue
        else:
            logging.debug(f"Baris {line_num} tidak cocok dengan format yang diharapkan, melanjutkan ke baris berikutnya.")

    # -- VALIDASI AKHIR DAN PEMBERSIHAN --
    logging.info(f"Melakukan pengecekan ulang terhadap {len(parsed_results)} hasil parsing...")
    
    # Pengecekan ulang format dan pembersihan
    cleaned_results = []
    for i, (label, justification) in enumerate(parsed_results):
        # Validasi format ulang
        if not label or not justification:
            logging.warning(f"Membuang hasil ke-{i+1}: label atau justifikasi kosong")
            continue
            
        # Validasi label masih ada di allowed_labels_set
        if label.upper() not in allowed_labels_set:
            logging.warning(f"Membuang hasil ke-{i+1}: label '{label}' tidak valid")
            continue
            
        # Validasi justifikasi tidak terlalu pendek
        if len(justification.strip()) < 3:
            logging.warning(f"Membuang hasil ke-{i+1}: justifikasi terlalu pendek: '{justification}'")
            continue
            
        cleaned_results.append((label, justification))
        
        # HENTIKAN JIKA SUDAH MENCAPAI JUMLAH YANG DIINGINKAN
        if len(cleaned_results) >= expected_count:
            logging.info(f"✓ Telah mengumpulkan {expected_count} hasil valid. Membuang {len(parsed_results) - i - 1} sisanya.")
            break
    
    # Pengecekan jumlah akhir
    if len(cleaned_results) != expected_count:
        error_msg = f"Validasi Gagal: Setelah pembersihan, jumlah hasil valid ({len(cleaned_results)}) tidak sesuai dengan input ({expected_count})."
        logging.warning(error_msg)
        logging.info(f"Hasil yang berhasil dibersihkan: {len(cleaned_results)}/{len(parsed_results)}")
        return False, error_msg

    structured_results = [{"label": r[0], "justification": r[1]} for r in cleaned_results]
    logging.info(f"✓ Validasi berhasil untuk {len(structured_results)} baris setelah pembersihan.")
    logging.info(f"Rasio pembersihan: {len(cleaned_results)}/{len(parsed_results)} hasil dipertahankan.")
    
    return True, structured_results