import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
from pathlib import Path
import threading
import queue
import subprocess
from datetime import datetime

# --- SETUP PATH UNTUK IMPOR ---

class App(tk.Tk):
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Auto-Labeling Aistudio")
        self.geometry("900x600")

        # Pastikan folder 'datasets' ada
        self.datasets_dir = Path("datasets")
        self.datasets_dir.mkdir(exist_ok=True)
        
        self.process = None
        self.start_time = None

        style = ttk.Style(self)
        style.configure("TNotebook.Tab", padding=(10, 5), font=('Helvetica', 10))
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(padx=10, pady=10, expand=True, fill='both')

        self.home_frame = ttk.Frame(self.notebook, padding="10")
        self.prompt_frame = ttk.Frame(self.notebook, padding="10")
        self.results_frame = ttk.Frame(self.notebook, padding="10")
        self.help_frame = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.home_frame, text="Home")
        self.notebook.add(self.prompt_frame, text="Prompt Editor")
        self.notebook.add(self.results_frame, text="Hasil & Log")
        self.notebook.add(self.help_frame, text="Bantuan")

        self.create_home_tab()
        self.create_prompt_tab()
        self.create_results_tab()
        self.create_help_tab()

        self.log_queue = queue.Queue()
        self.after(100, self.process_log_queue)

    def create_home_tab(self):
        content_frame = ttk.LabelFrame(self.home_frame, text="Operasi Utama", padding="10")
        content_frame.pack(fill='x', expand=False)
        
        self.mode_var = tk.StringVar(value="file")
        ttk.Radiobutton(content_frame, text="Satu File", variable=self.mode_var, value="file", command=self.toggle_mode).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Radiobutton(content_frame, text="Satu Folder", variable=self.mode_var, value="folder", command=self.toggle_mode).grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(content_frame, text="Path Input (dari dalam folder 'datasets'):").grid(row=1, column=0, sticky='w', pady=(10,0))
        self.input_path_var = tk.StringVar()
        self.input_path_entry = ttk.Entry(content_frame, textvariable=self.input_path_var, state='readonly', width=60)
        self.input_path_entry.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.file_button = ttk.Button(content_frame, text="Pilih File", command=self.select_file)
        self.file_button.grid(row=2, column=2, sticky='e', padx=5, pady=5)
        self.folder_button = ttk.Button(content_frame, text="Pilih Folder", command=self.select_folder)
        
        params_frame = ttk.LabelFrame(self.home_frame, text="Parameter Eksekusi", padding="10")
        params_frame.pack(fill='x', expand=False, pady=10)
        
        ttk.Label(params_frame, text="Ukuran Batch:").grid(row=0, column=0, sticky='w')
        self.batch_size_var = tk.StringVar(value="50")
        ttk.Entry(params_frame, textvariable=self.batch_size_var, width=10).grid(row=0, column=1, sticky='w')

        self.debug_var = tk.BooleanVar()
        ttk.Checkbutton(params_frame, text="Mode Debug", variable=self.debug_var).grid(row=0, column=2, sticky='w', padx=20)
        
        ttk.Label(params_frame, text="Label yang Diizinkan (pisahkan koma):").grid(row=1, column=0, sticky='w', pady=(10,0))
        self.labels_var = tk.StringVar(value="POSITIF,NEGATIF,NETRAL,TIDAK RELEVAN")
        ttk.Entry(params_frame, textvariable=self.labels_var, width=60).grid(row=2, column=0, columnspan=3, sticky='ew', pady=5)
        
        # Omitted allowed labels for now to focus on the folder logic
        action_frame = ttk.Frame(self.home_frame, padding="10")
        action_frame.pack(fill='x', expand=False)
        
        self.start_button = ttk.Button(action_frame, text="Mulai Proses", command=self.start_process, style="Accent.TButton")
        self.start_button.pack(side='left', padx=10)
        self.stop_button = ttk.Button(action_frame, text="Hentikan", command=self.stop_process, state='disabled')
        self.stop_button.pack(side='left', padx=10)

        self.toggle_mode()

    def create_prompt_tab(self):
        # 1. Label dan Kotak Input untuk Path File
        ttk.Label(self.prompt_frame, text="Path File Prompt:").pack(anchor='w')
        self.prompt_path_var = tk.StringVar(value="prompts/prompt.txt")
        ttk.Entry(self.prompt_frame, textvariable=self.prompt_path_var, width=70).pack(fill='x', expand=True)

        # 2. Tombol untuk Aksi
        button_frame = ttk.Frame(self.prompt_frame)
        button_frame.pack(anchor='w', pady=5)
        ttk.Button(button_frame, text="Muat Prompt", command=self.load_prompt).pack(side='left')
        ttk.Button(button_frame, text="Simpan Prompt", command=self.save_prompt).pack(side='left', padx=10)

        # 3. Kotak Teks Multi-baris untuk Konten Prompt
        self.prompt_text = tk.Text(self.prompt_frame, wrap='word', height=15)
        self.prompt_text.pack(fill='both', expand=True, pady=(5,0))
        
        # 4. Memuat prompt default saat aplikasi pertama kali dijalankan
        self.load_prompt()

    def create_results_tab(self):
        # Frame untuk informasi waktu
        info_frame = ttk.LabelFrame(self.results_frame, text="Informasi Eksekusi", padding="10")
        info_frame.pack(fill='x', pady=5)
        
        # Variabel untuk menampilkan waktu
        self.start_time_var = tk.StringVar(value="Waktu Mulai: -")
        self.end_time_var = tk.StringVar(value="Waktu Selesai: -")
        self.duration_var = tk.StringVar(value="Durasi: -")
        ttk.Label(info_frame, textvariable=self.start_time_var).pack(anchor='w')
        ttk.Label(info_frame, textvariable=self.end_time_var).pack(anchor='w')
        ttk.Label(info_frame, textvariable=self.duration_var).pack(anchor='w')

        # Frame untuk daftar file hasil
        results_frame = ttk.LabelFrame(self.results_frame, text="File Hasil", padding="10")
        results_frame.pack(fill='x', pady=5)
        ttk.Button(results_frame, text="Refresh Daftar", command=self.refresh_results).pack(anchor='w')
        self.results_listbox = tk.Listbox(results_frame, height=8)
        self.results_listbox.pack(fill='x', expand=True, pady=5)

        log_frame = ttk.LabelFrame(self.results_frame, text="Log Proses Real-time", padding="10")
        log_frame.pack(fill='both', expand=True, pady=5)
        
        # Buat widget
        self.log_text = tk.Text(log_frame, wrap='word', state='disabled', height=10)
        self.log_text.pack(fill='both', expand=True)

    def create_help_tab(self):
        help_text_content = """
Selamat Datang di Aplikasi Auto-Labeling!

Panduan ini akan membantu Anda menggunakan aplikasi secara efektif.

---------------------------------
TAB HOME: MEMULAI PROSES
---------------------------------

1.  Pilih Mode Operasi:
    -   Satu File: Pilih ini jika Anda ingin melabeli satu file data saja.
    -   Satu Folder: Pilih ini jika Anda telah memecah dataset besar menjadi beberapa file di dalam satu folder.

2.  Pilih Input:
    -   Tombol "Pilih..." akan membuka dialog yang terbatas pada folder 'datasets/'.
    -   Pastikan file atau folder yang ingin Anda proses berada di dalam 'datasets/'.
    -   Struktur yang disarankan:
        -   Untuk file tunggal: datasets/data_utama.csv
        -   Untuk banyak file: datasets/batch_data/file_01.csv, datasets/batch_data/file_02.csv, dst.

3.  Atur Parameter:
    -   Ukuran Batch: Jumlah baris yang dikirim ke AI dalam satu kali permintaan. Angka yang lebih kecil (misal: 25-50) lebih stabil tetapi lebih lambat. Angka yang lebih besar (misal: 100) lebih cepat tetapi lebih berisiko gagal.
    -   Mode Debug: Jika dicentang, aplikasi hanya akan memproses SATU batch dari setiap file lalu berhenti. Sangat berguna untuk pengujian cepat.
    -   Label yang Diizinkan: Masukkan semua label kategori yang Anda inginkan, dipisahkan dengan koma (contoh: POSITIF,NEGATIF,NETRAL). Ini SANGAT PENTING untuk validasi output.

4.  Mulai Proses:
    -   Klik "Mulai Proses" untuk memulai. Tombol akan nonaktif selama proses berjalan.
    -   Anda dapat memantau kemajuan di tab "Hasil & Log".

---------------------------------
TAB PROMPT EDITOR
---------------------------------

-   Gunakan tab ini untuk melihat, mengedit, dan menyimpan instruksi (prompt) yang akan diberikan kepada AI.
-   Aplikasi akan menggunakan file 'prompts/prompt.txt' secara default.
-   Untuk menggunakan prompt lain, ketik path-nya, klik "Muat Prompt", lalu "Simpan Prompt" sebagai 'prompts/prompt.txt'.

---------------------------------
TAB HASIL & LOG
---------------------------------

-   Informasi Eksekusi: Menampilkan ringkasan waktu mulai, selesai, dan total durasi proses terakhir.
-   File Hasil:
    -   Menampilkan daftar file yang telah selesai diproses di folder 'results/'.
    -   Jika Anda menggunakan mode "Satu Folder", ia akan menampilkan isi dari subfolder hasil yang sesuai.
    -   Klik "Refresh Daftar" untuk memperbarui tampilan.
-   Log Proses Real-time: Menampilkan output konsol dari proses backend saat sedang berjalan. Sangat berguna untuk melihat apa yang sedang terjadi.

---------------------------------
OUTPUT YANG DIHASILKAN
---------------------------------

1.  Folder 'results/':
    -   Mode File Tunggal: Akan menghasilkan file seperti 'nama_file_labeled_TIMESTAMP.csv'.
    -   Mode Folder: Akan menghasilkan subfolder seperti 'results/nama_folder/' yang berisi semua file yang telah dilabeli.

2.  Folder 'logs/':
    -   Setiap kali aplikasi dijalankan, sebuah folder baru dengan stempel waktu akan dibuat.
    -   Di dalamnya terdapat log teks lengkap, screenshot jika terjadi error, dan file 'check_data' untuk analisis mendalam. Ini adalah sumber utama untuk pemecahan masalah.
"""
        help_text_widget = tk.Text(self.help_frame, wrap='word', state='disabled', padx=5, pady=5)
        help_text_widget.pack(fill='both', expand=True)
        help_text_widget.configure(state='normal')
        help_text_widget.insert('1.0', help_text_content)
        help_text_widget.configure(state='disabled')

    # --- FUNGSI LOGIKA BARU ---
    def select_file(self):
        # Membuka dialog HANYA di dalam folder 'datasets'
        filepath = filedialog.askopenfilename(
            title="Pilih satu file dari folder datasets",
            initialdir=self.datasets_dir,
            filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
        )
        if filepath:
            # Hanya simpan path relatif dari folder datasets
            relative_path = Path(filepath).relative_to(self.datasets_dir.resolve())
            self.input_path_var.set(f"datasets/{relative_path}")

    def select_folder(self):
        # Membuka dialog HANYA di dalam folder 'datasets'
        folderpath = filedialog.askdirectory(
            title="Pilih satu folder dari dalam folder datasets",
            initialdir=self.datasets_dir
        )
        if folderpath:
            # Hanya simpan path relatif dari folder datasets
            relative_path = Path(folderpath).relative_to(self.datasets_dir.resolve())
            self.input_path_var.set(f"datasets/{relative_path}")
            
    def start_process(self):
        input_path_str = self.input_path_var.get()
        if not input_path_str:
            messagebox.showerror("Input Tidak Lengkap", "Harap pilih file atau folder dari dalam 'datasets'.")
            return

        # --- VALIDASI PARAMETER ---
        try:
            batch_size = int(self.batch_size_var.get())
            if batch_size <= 0:
                raise ValueError("Ukuran batch harus lebih besar dari nol.")
        except ValueError as e:
            messagebox.showerror("Input Tidak Valid", f"Ukuran Batch tidak valid. Harap masukkan angka positif.\n\nDetail: {e}")
            return
        # --- AKHIR VALIDASI ---

        allowed_labels_str = self.labels_var.get()
        if not allowed_labels_str or not allowed_labels_str.strip():
            messagebox.showerror("Input Tidak Valid", "Daftar 'Label yang Diizinkan' tidak boleh kosong.")
            return
        
        is_debug = self.debug_var.get()
        mode = self.mode_var.get()
        input_path = Path(input_path_str)
        files_to_process = []
        output_directory = None
        self.last_output_dir = None # Simpan path output terakhir untuk tab results

        if mode == 'file':
            if not input_path.is_file():
                messagebox.showerror("Error Path", f"Path yang dipilih bukan file: {input_path_str}")
                return
            files_to_process.append(input_path)
            
        else: # Mode folder
            if not input_path.is_dir():
                messagebox.showerror("Error Path", f"Path yang dipilih bukan folder: {input_path_str}")
                return
            
            files_to_process = sorted(list(input_path.glob('*.csv')) + list(input_path.glob('*.xlsx')))
            
            if not files_to_process:
                messagebox.showerror("Folder Kosong", f"Tidak ada file .csv atau .xlsx yang ditemukan di folder '{input_path.name}'.")
                return

            output_directory = Path("results") / input_path.name
            output_directory.mkdir(parents=True, exist_ok=True)
            self.last_output_dir = output_directory
            
            messagebox.showinfo("Proses Folder Dimulai", f"Ditemukan {len(files_to_process)} file.\nHasil akan disimpan di folder:\n{output_directory.resolve()}")
        
        # Perbarui UI
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert('1.0', "--- Proses Pelabelan Dimulai ---\n")
        self.log_text.config(state='disabled')
        
        self.start_time = datetime.now()
        self.start_time_var.set(f"Waktu Mulai: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Jalankan thread dengan parameter yang sudah divalidasi
        threading.Thread(target=self._run_backend_loop, args=(files_to_process, output_directory, batch_size, is_debug, allowed_labels_str), daemon=True).start()

    def stop_process(self):
        if self.process and self.process.poll() is None: # Periksa apakah proses ada dan masih berjalan
            response = messagebox.askyesno("Konfirmasi Hentikan", "Anda yakin ingin menghentikan proses yang sedang berjalan?")
            if response:
                self.log_queue.put("\n--- PENGGUNA MEMINTA UNTUK MENGHENTIKAN PROSES ---\n")
                self.process.terminate() # Hentikan proses backend
                # Kita tidak langsung memperbarui UI di sini. 
                # Kita tunggu sinyal 'None' dari queue, seolah-olah proses selesai secara normal.
                self.log_queue.put("--- PROSES DIHENTIKAN SECARA PAKSA ---\n")

    def _run_backend_loop(self, files_to_process, output_dir, batch_size, is_debug, allowed_labels):
        total_files = len(files_to_process)
        for i, file_path in enumerate(files_to_process):
            self.log_queue.put(f"\n{'='*20}\nMEMPROSES FILE {i+1}/{total_files}: {file_path.name}\n{'='*20}\n")
            
            # Membangun perintah subprocess LENGKAP
            command = [
                sys.executable, str(Path("src/main.py")),
                "--input-file", str(file_path),
                "--batch-size", str(batch_size),
                "--allowed-labels", allowed_labels
            ]
            if is_debug: 
                command.append("--debug")
            
            # Tambahkan output directory untuk mode folder
            if output_dir:
                command.extend(["--output-dir", str(output_dir)])
            
            self.process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            try:
                for line in iter(self.process.stdout.readline, ''):
                    self.log_queue.put(line)
            except UnicodeDecodeError as e:
                error_msg = f"Unicode decode error: {e}. Menggunakan fallback decoding..."
                self.log_queue.put(error_msg)
                # Fallback: read as bytes and decode with error handling
                for raw_line in iter(self.process.stdout.readline, b''):
                    try:
                        line = raw_line.decode('utf-8', errors='replace')
                        self.log_queue.put(line)
                    except Exception as decode_err:
                        self.log_queue.put(f"Failed to decode line: {decode_err}\n")
            
            self.process.stdout.close()
            return_code = self.process.wait()

            if return_code != 0:
                self.log_queue.put(f"\nERROR: Proses untuk file {file_path.name} selesai dengan error. Lanjut ke file berikutnya.\n")
            else:
                 self.log_queue.put(f"\nSUKSES: File {file_path.name} selesai diproses.\n")

        self.log_queue.put(None)

    # ... (Sisa fungsi seperti toggle_mode, process_log_queue, process_finished, dll. tetap sama) ...
    def toggle_mode(self):
        if self.mode_var.get() == "file":
            self.file_button.grid()
            self.folder_button.grid_remove()
        else:
            self.file_button.grid_remove()
            self.folder_button.grid()

    def load_prompt(self):
        # 1. Mendapatkan path file dari kotak input
        path = self.prompt_path_var.get()
        try:
            # 2. Membaca file
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                # 3. Menghapus konten lama dan memasukkan konten baru ke kotak teks
                self.prompt_text.delete('1.0', tk.END)
                self.prompt_text.insert('1.0', f.read())
        except FileNotFoundError:
            # 4. Menampilkan peringatan jika file tidak ada
            messagebox.showwarning("File Tidak Ditemukan", f"File prompt di {path} tidak ditemukan.")
        except UnicodeDecodeError as e:
            messagebox.showerror("Encoding Error", f"Tidak dapat membaca file karena masalah encoding: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error tidak terduga saat membaca file: {e}")

    def save_prompt(self):
        # 1. Mendapatkan path file dari kotak input
        path_str = self.prompt_path_var.get()
        # Membuat direktori jika belum ada (misalnya 'prompts/')
        Path(path_str).parent.mkdir(parents=True, exist_ok=True)

        # 2. Mendapatkan konten teks yang sudah diedit dari kotak teks
        content = self.prompt_text.get('1.0', tk.END)
        try:
            # 3. Menulis konten baru ke file
            with open(path_str, 'w', encoding='utf-8', errors='replace') as f:
                f.write(content)
            # 4. Memberikan konfirmasi kepada pengguna
            messagebox.showinfo("Sukses", f"Prompt berhasil disimpan ke {path_str}.")
        except Exception as e:
            # 5. Menampilkan error jika penyimpanan gagal
            messagebox.showerror("Error", f"Gagal menyimpan prompt: {e}")

    def refresh_results(self, result_folder="results"):
        # Secara default, lihat folder 'results/' utama
        folder_to_show = Path("results")

        # Jika proses terakhir adalah mode folder, ubah path target
        # Kita simpan path output di instance saat proses dimulai
        if hasattr(self, 'last_output_dir') and self.last_output_dir:
            folder_to_show = self.last_output_dir

        self.results_listbox.delete(0, tk.END)
        self.results_listbox.insert(tk.END, f"Menampilkan isi dari: ./{folder_to_show}")
        self.results_listbox.insert(tk.END, "-"*50)
        
        if folder_to_show.is_dir():
            # Tampilkan folder dan file
            for f in sorted(folder_to_show.iterdir()):
                prefix = "[FOLDER] " if f.is_dir() else ""
                self.results_listbox.insert(tk.END, prefix + f.name)
        else:
            self.results_listbox.insert(tk.END, "Folder hasil belum dibuat.")
    
    def process_log_queue(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                if line is None:
                    self.process_finished()
                    return
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, line)
                self.log_text.see(tk.END)
                self.log_text.config(state='disabled')
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)

    def process_finished(self):
        was_terminated = self.process and self.process.returncode != 0
        
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else "N/A"
        
        self.end_time_var.set(f"Waktu Selesai: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.start_time:
            self.duration_var.set(f"Durasi: {str(duration).split('.')[0]}")
        
        self.refresh_results()
        
        # Hanya tampilkan pesan sukses jika proses selesai secara normal
        if was_terminated:
            messagebox.showwarning("Proses Dihentikan", "Proses telah dihentikan oleh pengguna.")
        else:
            messagebox.showinfo("Selesai", "Semua pekerjaan telah selesai.")

        self.process = None # Reset objek proses

if __name__ == "__main__":
    app = App()
    app.mainloop()