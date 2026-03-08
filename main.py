import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from datetime import datetime, date

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



# === Membuat dan Connect 'SQLAlchemy Engine' dari Konfigurasi di File .env ===
def create_engine_from_env():
    load_dotenv()

    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT", "3306")

    try:
        url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(url)

        with engine.connect() as _:
            pass

        print("Koneksi ke database berhasil.")
        return engine
    
    except Exception as e:
        print("Gagal terhubung ke database.")
        print(f"Detail error: '{e}'")
        return None

# === Input 'ANGKA' Aman Agar Program Tidak Crash Jika User Salah Input ===
def safe_int_input(prompt: str, pilihan_valid=None) -> int:
    while True:
        user_input = input(prompt).strip()
        
        if user_input == "":
            print("Input tidak boleh kosong. Coba lagi.\n")
            continue

        if not user_input.isdigit():
            print("Input harus angka bulat. Coba lagi.\n")
            continue

        angka = int(user_input)

        if pilihan_valid is not None and angka not in pilihan_valid:
            print(f"Pilihan tidak valid. Pilih salah satu: {sorted(pilihan_valid)}\n")
            continue

        return angka

# === Input 'TANGGAL' Aman dengan Format YYYY-MM-DD ===
def safe_date_input(prompt: str) -> date:
    while True:
        date_str = input(prompt).strip()

        if date_str == "0":
            return None

        if date_str == "":
            today = datetime.now().date()
            print(f"\nBerhasil input menggunakan tanggal hari ini: {today}")
            return today

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return parsed_date
        
        except ValueError:
            print("Format tanggal harus YYYY-MM-DD. (Contoh: 2026-12-01)\n")

# === Input 'AMOUNT' Aman (Boleh INT / FLOAT) dengan Syarat > 0 ===
def safe_amount_input(prompt: str) -> float:
    while True:
        amount_str = input(prompt).strip()

        if amount_str == "":
            print("Input tidak boleh kosong.")
            continue

        if amount_str == "0":
            return None
        
        try:
            amount = float(amount_str)
        except ValueError:
            print("Amount harus berupa angka. (Contoh: 50000)")
            continue

        if amount <= 0:
            print("Amount harus lebih dari 0.")
            continue

        return amount

# === Input 'FLOW' Aman dengan Pilihan Valid (IN/OUT) ===
def safe_flow_input(prompt: str = "Masukkan flow (IN/OUT): ") -> str:
    while True:
        flow = input(prompt).strip().upper()

        if flow == "0":
            return None

        if flow == "":
            print("Input tidak boleh kosong.")
            continue

        if flow in ("IN", "OUT"):
            return flow
        
        print('Flow harus "IN" / "OUT" / "0" (Batal).')

# === Input 'KONFIRMASI' Aman (Y/N) -> (Return: True jika Y, False jika N) ===
def safe_confirm_input(prompt: str) -> bool:
    while True:
        confirm = input(prompt).strip().upper()

        if confirm == "":
            print('Input tidak boleh kosong. Masukkan "Y" atau "N".')
            continue

        if confirm == "Y":
            return True
        
        if confirm == "N":
            return False
        
        print('Input harus "Y" atau "N".')

# === Menjalankan Query 'SELECT' ===
def run_select_df(engine, query: str, params=None) -> pd.DataFrame:
    """
    - query: string SQL
    - params: dict untuk parameter query (Ex: {"limit": 20})
    'parameter' dipakai jika query butuh parameter tambahan (Ex: LIMIT :limit)
    """
    try:
        sql_query = text(query)
        df = pd.read_sql(sql_query, engine, params=params)
        return df
    
    except Exception as e:
        print("Query gagal dijalankan")
        print(f"Detail error: {e}\n")
        return pd.DataFrame()
    
# === Menjalankan Query 'Non-SELECT' (INSERT / UPDATE / DELETE) ===
def run_execute(engine, query: str, params=None) -> bool:
    """
    engine.begin() akan otomatis COMMIT jika tidak ada error,
    dan akan otomatis ROLLBACK jika ada error.
    """
    try:
        sql = text(query)
        with engine.begin() as connection:
            connection.execute(sql, params or {})
        return True
    
    except Exception as e:
        print("Query gagal dijalankan.")
        print(f"Detail error: {e}\n")
        return False

# === Menampilkan 'DATAFRAME' ===
def show_dataframe(df: pd.DataFrame) -> None:
    if df.empty:
        print("(Data kosong / tidak ada baris.)\n")
        return
    
    print(df.to_string(index=False))
    print("")

# === Menerapkan format rupiah dengan "." sebagai pemisah angka ===
def format_rupiah(amount: float) -> str:
    formatted = f"{amount:,.0f}"
    return f"Rp {formatted.replace(',', '.')}"

# === Formatter rupiah untuk label axis chart ===
def rupiah_axis_formatter(x, pos):
    return f"Rp {x:,.0f}".replace(',', '.')

# ===========================================================
#                    FEATURE 1: SHOW TABLE
# ===========================================================

# === Menampilkan Tabel CATEGORIES ===
def show_categories(engine, flow=None) -> pd.DataFrame:
    if flow is None:
        print("\n---- TABEL KATEGORI (SEMUA) ----")
        query = """
            SELECT category_id, category_name, flow
            FROM categories
            ORDER BY category_id
        """
        df = run_select_df(engine, query)
        show_dataframe(df)
        return df
    
    flow = flow.upper().strip()

    print(f"\n------ TABEL KATEGORI {flow} ------")
    query = """
        SELECT category_id, category_name, flow
        FROM categories
        WHERE flow = :flow
        ORDER BY category_id
    """
    df = run_select_df(engine, query, params={"flow": flow})
    show_dataframe(df)
    return df

# === Menampilkan Tabel TRANSACTIONS (JOIN category_name) ALL DATA ===
def show_transactions_view_all(engine) -> None:
    print(f"\n------------------------------ TABEL TRANSAKSI (SEMUA) ------------------------------")
    query = """
        SELECT
            t.trx_id,
            t.trx_date,
            t.flow,
            c.category_name,
            t.amount,
            t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.trx_date DESC, t.trx_id DESC
    """
    df = run_select_df(engine, query)

    if df.empty:
        print("(Data kosong / tidak ada baris.)")
        return

    df_display = df.copy()
    df_display["amount"] = df_display["amount"].apply(format_rupiah)
    show_dataframe(df_display)

# === Menampilkan Tabel TRANSACTIONS (JOIN category_name) dengan Default LIMIT: 20 ===
def show_transactions_latest(engine, limit: int = 20) -> None:
    print(f"\n---------------------------- TABEL TRANSAKSI (TERBARU {limit}) --------------------------")
    query = """
        SELECT
            t.trx_id,
            t.trx_date,
            t.flow,
            c.category_name,
            t.amount,
            t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.trx_date DESC, t.trx_id DESC
        LIMIT :limit
    """
    df = run_select_df(engine, query, params={"limit": limit})

    if df.empty:
        print("(Data kosong / tidak ada baris.)")
        return

    df_display = df.copy()
    df_display["amount"] = df_display["amount"].apply(format_rupiah)
    show_dataframe(df_display)

# === Menampilkan Table TRANSACTIONS by FLOW (IN / OUT) dengan Default LIMIT: 20 ===
def show_transactions_filter_flow(engine, flow: str, limit: int = 20) -> None:
    flow = flow.upper().strip()
    
    print(f"\n---------------------- TABEL TRANSAKSI (FLOW {flow} - LIMIT {limit}) ----------------------")
    query = """
        SELECT
            t.trx_id,
            t.trx_date,
            t.flow,
            c.category_name,
            t.amount,
            t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.flow = :flow
        ORDER BY t.trx_date DESC, t.trx_id DESC
        LIMIT :limit
    """
    df = run_select_df(engine, query, params={"flow": flow, "limit": limit})

    if df.empty:
        print("(Data kosong / tidak ada baris.)")
        return

    df_display = df.copy()
    df_display["amount"] = df_display["amount"].apply(format_rupiah)
    show_dataframe(df_display)

# ========== OPSI MENU 1: SHOW TABLE ==========
def show_table_menu(engine) -> None:
    while True:
        print("\n=== Menu 1: TAMPILKAN TABEL ===")
        print("1. Tabel Kategori")
        print("2. Tabel Transaksi")
        print("0. Kembali\n")

        choice = safe_int_input("Pilih menu (0-2): ", range(3))

        if choice == 1:
            while True:
                print("\n--- Sub-Menu 1: TABEL KATEGORI ---")
                print("1. Lihat Semua Kategori")
                print("2. Lihat Kategori IN")
                print("3. Lihat Kategori OUT")
                print("0. Kembali\n")

                sub = safe_int_input("Pilih menu (0-3): ", range(4))

                if sub == 1:
                    show_categories(engine)
                elif sub == 2:
                    show_categories(engine, flow="IN")
                elif sub == 3:
                    show_categories(engine, flow="OUT")
                else:
                    break

        elif choice == 2:
            while True:
                print("\n-------- Sub-Menu 2: TABEL TRANSAKSI -------")
                print("1. Lihat Semua Transaksi")
                print("2. Lihat Transaksi Terbaru (20)")
                print("3. Lihat Transaksi berdasarkan Flow (IN/OUT)")
                print("0. Kembali\n")

                sub = safe_int_input("Pilih menu (0-3): ", range(4))

                if sub == 1:
                    show_transactions_view_all(engine)
                elif sub == 2:
                    show_transactions_latest(engine)
                elif sub == 3:
                    flow = safe_flow_input("\nMasukkan flow (IN/OUT/0=Batal): ")
                    if flow is None:
                        continue
                    show_transactions_filter_flow(engine, flow)
                else:
                    break

        else:
            return

# ===========================================================
#                   FEATURE 2: SHOW STATISTIK
# ===========================================================

# === Menampilkan Basic STATISTIK (COUNT, SUM, AVG) by FLOW (ALL / IN / OUT) ===
def get_basic_stats(engine, flow=None) -> tuple[int, float, float]:
    """
    flow:
    - None -> ALL
    - "IN" -> Hanya transaksi IN
    - "OUT" -> Hanya transaksi OUT
    """
    if flow is None:
        query = """
            SELECT
                COUNT(*) AS total_transaksi,
                SUM(amount) AS total_amount,
                AVG(amount) AS avg_amount
            FROM transactions
        """
        params = None
    
    else:
        query = """
            SELECT
                COUNT(*) AS total_transaksi,
                SUM(amount) AS total_amount,
                AVG(amount) AS avg_amount
            FROM transactions
            WHERE flow = :flow
        """
        params = {"flow": flow}

    df = run_select_df(engine, query, params=params)

    if df.empty:
        print("(Gagal mengambil data statistik dari database.)")
        return 0, 0, 0

    total_trx = df.loc[0, "total_transaksi"] or 0
    total_amount = df.loc[0, "total_amount"] or 0
    avg_amount = df.loc[0, "avg_amount"] or 0

    return total_trx, total_amount, avg_amount

# === Menampilkan DATAFRAME STATISTIK per KATEGORI by FLOW (IN / OUT) ===
def show_stats_per_category_by_flow(engine, flow: str) -> None:
    flow = flow.upper().strip()

    print(f"\n------------ STATISTIK PER KATEGORI ({flow}) ----------")

    query = """
        SELECT
            c.category_name,
            COUNT(*) AS trx_count,
            SUM(t.amount) AS total_amount,
            AVG(t.amount) AS avg_amount
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.flow = :flow
        GROUP BY c.category_name
        ORDER BY total_amount DESC
    """

    df = run_select_df(engine, query, params={"flow": flow})

    if df.empty:
        print("(Data kosong / tidak ada baris.)")
        return
    
    df_display = df.copy()
    df_display["total_amount"] = df_display["total_amount"].apply(format_rupiah)
    df_display["avg_amount"] = df_display["avg_amount"].apply(format_rupiah)
    show_dataframe(df_display)

# ========== OPSI MENU 2: SHOW STATISTIK ==========
def show_statistik_menu(engine) -> None:
    while True:
        print("\n===== Menu 2: TAMPILKAN STATISTIK =====")
        print("1. Lihat Semua Statistik")
        print("2. Lihat Statistik IN")
        print("3. Lihat Statistik OUT")
        print("4. Lihat Statistik per Kategori (IN)")
        print("5. Lihat Statistik per Kategori (OUT)")
        print("0. Kembali\n")

        choice = safe_int_input("Pilih menu (0-5): ", range(6))
        
        if choice == 1:
            total_trx, total_amount, avg_amount = get_basic_stats(engine, flow=None)
            print("\n--------- STATISTIK SEMUA ---------")
            print(f"Total Transaksi    : {total_trx}")
            print(f"Total Nominal      : {format_rupiah(total_amount)}")
            print(f"Rata-Rata Nominal  : {format_rupiah(avg_amount)}")

        elif choice == 2:
            total_trx, total_amount, avg_amount = get_basic_stats(engine, flow="IN")
            print("\n---------- STATISTIK IN ----------")
            print(f"Total Transaksi   : {total_trx}")
            print(f"Total Nominal     : {format_rupiah(total_amount)}")
            print(f"Rata-Rata Nominal : {format_rupiah(avg_amount)}")

        elif choice == 3:
            total_trx, total_amount, avg_amount = get_basic_stats(engine, flow="OUT")
            print("\n--------- STATISTIK OUT ---------")
            print(f"Total Transaksi    : {total_trx}")
            print(f"Total Nominal      : {format_rupiah(total_amount)}")
            print(f"Rata-Rata Nominal  : {format_rupiah(avg_amount)}")

        elif choice == 4:
            show_stats_per_category_by_flow(engine, "IN")

        elif choice == 5:
            show_stats_per_category_by_flow(engine, "OUT")

        else:
            return

# ===========================================================
#                FEATURE 3: DATA VISUALIZATION
# ===========================================================

# === Menampilkan 'HISTOGRAM' untuk Kolom AMOUNT dari Tabel TRANSACTIONS ===
def plot_histogram_amount(engine) -> None:
    query = """
        SELECT amount, flow
        FROM transactions
    """
    df = run_select_df(engine, query)

    if df.empty:
        print("(Data transaksi kosong, histogram tidak dapat ditampilkan.)\n")
        return

    plt.figure(figsize=(10, 5))
    sns.histplot(data=df, x="amount", bins=15, hue="flow", multiple="stack")

    plt.title("Diatribusi Nominal Transaksi (IN vs OUT)")
    plt.xlabel("Nominal Transaksi")
    plt.ylabel("Jumlah Transaksi")

    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(rupiah_axis_formatter))
    plt.tight_layout()
    plt.show()
    plt.close()

# === Menampilkan 'BAR PLOT' Top 5 KATEGORI OUT Berdasarkan TOTAL AMOUNT (SUM) ===
def plot_top5_out_categories(engine) -> None:
    query = """
        SELECT
            c.category_name,
            SUM(t.amount) AS total_out
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.flow = 'OUT'
        GROUP BY c.category_name
        ORDER BY total_out DESC
        LIMIT 5
    """
    df = run_select_df(engine, query)

    if df.empty:
        print("(Tidak ada data untuk ditampilkan.)\n")
        return
    
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=df, x="total_out", y="category_name")

    plt.title("Top 5 Kategori Pengeluaran Terbesar")
    plt.xlabel("Total Pengeluaran")
    plt.ylabel("Kategori")

    ax.xaxis.set_major_formatter(plt.FuncFormatter(rupiah_axis_formatter))
    plt.tight_layout()
    plt.show()
    plt.close()

# ========== OPSI MENU 3: DATA VISUALIZATION ==========
def show_visualization_menu(engine) -> None:
    while True:
        print("\n============ Menu 3: Visualisasi Data ===========")
        print("1. Distribusi Nominal Transaksi (Histogram)")
        print("2. Top 5 Kategori Pengeluaran Terbesar (Bar Plot)")
        print("0. Kembali\n")

        choice = safe_int_input("Pilih menu (0-2): ", range(3))

        if choice == 1:
            plot_histogram_amount(engine)
        elif choice == 2:
            plot_top5_out_categories(engine)
        else:
            return
        
# ===========================================================
#                     FEATURE 4: ADD DATA
# ===========================================================

# === ADD DATA Transaksi ke Tabel TRANSACTIONS ===
def add_transaction(engine) -> None:
    """
    Flow:
    1) Input trx_date
    2) Input amount
    3) Input flow (IN / OUT)
    4) Pilih category_id (Tampilkan categories dulu)
    5) Input note (Opsional. Boleh kosong)
    6) INSERT ke table transactions
    """
    print("\n--------------------- TAMBAH TRANSAKSI ---------------------")

    trx_date = safe_date_input("Masukkan trx_date (YYYY-MM-DD) [Enter = Tanggal hari ini, 0=Batal]: ")
    if trx_date is None:
        print("\nTambah Transaksi dibatalkan.")
        return
    
    amount = safe_amount_input("\nMasukkan amount (> 0) [0=Batal]: ")
    if amount is None:
        print("\nTambah Transaksi dibatalkan.")
        return

    flow = safe_flow_input("\nMasukkan flow transaksi (IN/OUT/0=Batal): ")
    if flow is None:
        print("\nTambah Transaksi dibatalkan.")
        return

    print("\nDaftar Kategori (Sesuai flow transaksi):")
    df_cat = show_categories(engine, flow=flow)

    if df_cat.empty:
        print(f"Tambahkan kategori flow {flow} terlebih dahulu.\n")
        return
    
    valid_ids = set(df_cat["category_id"])

    while True:
        category_id = safe_int_input("Pilih category_id (0=Batal): ")

        if category_id == 0:
            print("\nTambah Transaksi dibatalkan.")
            return

        if category_id in valid_ids:
            break

        print("category_id tidak sesuai. Pilih dari daftar Tabel Kategori.")

    category_name = df_cat.loc[df_cat["category_id"] == category_id, "category_name"].values[0]

    note = input("\nMasukkan note (Opsional, Enter untuk skip): ").strip()
    if note == "":
        note = None

    query = """
        INSERT INTO transactions (trx_date, amount, flow, category_id, note)
        VALUES (:trx_date, :amount, :flow, :category_id, :note)
    """
    params = {
        "trx_date": trx_date,
        "amount": amount,
        "flow": flow,
        "category_id": category_id,
        "note": note
    }

    success = run_execute(engine, query, params=params)
    if success:
        print(f"\nTransaksi berhasil ditambahkan! ({category_name} | {flow} | {format_rupiah(amount)})")

# === ADD DATA New Category ke Tabel CATEGORIES ===
def add_category(engine) -> None:
    """
    Flow:
    1) Show tabel categories (ALL)
    2) Input nama category baru
    3) Validasi tidak boleh kosong
    4) Flow wajib IN atau OUT
    5) Handle duplicate (UNIQUE category_name)
    6) INSERT ke table categories
    """
    print("\n--------- TAMBAH KATEGORI ---------")
    print("Daftar Kategori saat ini:")
    show_categories(engine)

    print("Silakan tambah kategori baru.")

    while True:
        category_name = input("\nMasukkan category_name (0=Batal): ").strip()

        if category_name == "0":
            print("\nTambah Kategori dibatalkan.")
            return

        if category_name == "":
            print("category_name tidak boleh kosong.")
            continue

        if not all(c.isalpha() or c.isspace() for c in category_name):
            print("category_name hanya boleh berisi huruf dan spasi. (Contoh: Food, Daily Transport)")
            continue

        break

    flow = safe_flow_input("\nMasukkan flow category (IN/OUT/0=Batal): ")
    if flow is None:
        print("\nTambah Kategori dibatalkan.")
        return

    query = """
        INSERT INTO categories (category_name, flow)
        VALUES (:category_name, :flow)
    """

    try:
        with engine.begin() as connection:
            connection.execute(text(query), {"category_name": category_name, "flow": flow})
        
        print(f"\nKategori baru berhasil ditambahkan! ({category_name} | {flow})")
        print("\nDaftar Kategori terbaru:")
        show_categories(engine)

    except IntegrityError:
        print("\nKategori sudah ada (duplikat). Silakan pakai nama lain.")

    except Exception as e:
        print("\nGagal menambahkan kategori.")
        print(f"Detail error: {e}\n")

# ========== OPSI MENU 4: ADD DATA ==========
def add_data_menu(engine) -> None:
    while True:
        print("\n=== Menu 4: TAMBAH DATA ===")
        print("1. Tambah Transaksi")
        print("2. Tambah Kategori")
        print("0. Kembali\n")

        choice = safe_int_input("Pilih menu (0-2): ", range(3))

        if choice == 1:
            add_transaction(engine)
        elif choice == 2:
            add_category(engine)
        else:
            return
        
# ===========================================================
#                     FEATURE 5: DELETE DATA
# ===========================================================

# === DELETE DATA Transaksi dari Tabel TRANSACTIONS by trx_id ===
def delete_transaction(engine) -> None:
    """
    Flow:
    1) Tampilkan seluruh transaksi
    2) User pilih trx_id (0=Back)
    3) Validasi trx_id terdaftar
    4) Konfirmasi hapus
    5) Delete
    """
    print("\n--------------------------------- HAPUS TRANSAKSI --------------------------------")

    query_list_transaction = """
        SELECT
            t.trx_id,
            t.trx_date,
            t.flow,
            c.category_name,
            t.amount,
            t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        ORDER BY t.trx_date DESC, t.trx_id DESC
    """

    df = run_select_df(engine, query_list_transaction)

    if df.empty:
        print("(Tidak ada transaksi untuk dihapus.)")
        return

    df_display = df.copy()
    df_display["amount"] = df_display["amount"].apply(format_rupiah)
    show_dataframe(df_display)

    valid_ids = set(df["trx_id"])

    while True:
        trx_id = safe_int_input("Masukkan trx_id yang mau dihapus (0=Back): ")
        if trx_id == 0:
            print("Hapus transaksi dibatalkan.")
            return
        if trx_id in valid_ids:
            break
        print("trx_id tidak ditemukan. Pilih dari tabel di atas.")

    row = df[df["trx_id"] == trx_id].iloc[0]

    print(f"\nTransaksi yang akan dihapus:")
    print(f"ID       : {row['trx_id']}")
    print(f"Tanggal  : {row['trx_date']}")
    print(f"Flow     : {row['flow']}")
    print(f"Kategori : {row['category_name']}")
    print(f"Amount   : {format_rupiah(row['amount'])}")
    print(f"Note     : {row['note']}")

    if not safe_confirm_input("\nYakin hapus transaksi ini? (Y/N): "):
        print("\nHapus transaksi dibatalkan.")
        return
    
    query_delete_transaction = """
        DELETE FROM transactions
        WHERE trx_id = :trx_id
    """
    success = run_execute(engine, query_delete_transaction, params={"trx_id": trx_id})

    if success:
        print(f"\nTransaksi berhasil dihapus! (ID {trx_id} | {row['flow']} | {row['category_name']} | {format_rupiah(row['amount'])})")

# === DELETE DATA Category dari Tabel CATEGORIES by category_id ===
def delete_category(engine) -> None:
    """
    Flow:
    1) Tampilkan category_id terdaftar
    2) User pilih category_id (0=Back)
    3) Validasi category_id terdaftar
    4) Validasi gagal hapus category jika masih dipakai di tabel transactions
    5) Konfirmasi hapus
    6) Delete
    """
    print("\n------- HAPUS KATEGORI -------")

    query_list_category = """
        SELECT category_id, category_name, flow
        FROM categories
        ORDER BY category_id
    """
    df = run_select_df(engine, query_list_category)

    if df.empty:
        print("(Tidak ada kategori untuk dihapus.)")
        return
    
    show_dataframe(df)
    
    valid_ids = set(df["category_id"])

    while True:
        category_id = safe_int_input("Masukkan category_id yang mau dihapus (0=Back): ")
        if category_id == 0:
            print("\nHapus kategori dibatalkan.")
            return
        if category_id in valid_ids:
            break
        print("category_id tidak ada di daftar. Pilih dari tabel kategori yang ditampilkan.\n")

    row = df[df['category_id'] == category_id].iloc[0]

    print(f"\nKategori yang akan dihapus:")
    print(f"ID   : {row['category_id']}")
    print(f"Nama : {row['category_name']}")
    print(f"Flow : {row['flow']}")

    if not safe_confirm_input("\nYakin hapus kategori ini? (Y/N): "):
        print("\nHapus kategori dibatalkan.")
        return
    
    query_delete_category = """
        DELETE FROM categories
        WHERE category_id = :category_id
    """

    try:
        with engine.begin() as connection:
            connection.execute(text(query_delete_category), {"category_id": category_id})

        print(f"\nKategori berhasil dihapus! ({row['category_name']} | {row['flow']})")

    except Exception as e:
        print("Gagal menghapus kategori.")
        print("Kemungkinan kategori masih dipakai di tabel transaksi.")
        print(f"Detail error: {e}")

# ========== OPSI MENU 5: DELETE DATA ==========
def delete_data_menu(engine) -> None:
    while True:
        print("\n=== Menu 5: HAPUS DATA ===")
        print("1. Hapus Transaksi")
        print("2. Hapus Kategori")
        print("0. Kembali\n")

        choice = safe_int_input("Pilih menu (0-2): ", range(3))

        if choice == 1:
            delete_transaction(engine)
        elif choice == 2:
            delete_category(engine)
        else:
            return

# ===========================================================
#                      MAIN PROGRAM MENU
# ===========================================================

def main() -> None:
    print("\n======= Xpense Insight =======")

    engine = create_engine_from_env()
    if engine is None:
        print("\nProgram berhenti karena tidak bisa terhubung ke database.")
        return
    
    try:
        while True:
            print("\n====== MAIN MENU ======")
            print("1. Tampilkan Tabel")
            print("2. Tampilkan Statistik")
            print("3. Visualisasi Data")
            print("4. Tambah Data")
            print("5. Hapus Data")
            print("0. Keluar")
            print("=======================\n")

            choice = safe_int_input("Pilih menu (0-5): ", range(6))

            if choice == 1:
                show_table_menu(engine)
            elif choice == 2:
                show_statistik_menu(engine)
            elif choice == 3:
                show_visualization_menu(engine)
            elif choice == 4:
                add_data_menu(engine)
            elif choice == 5:
                delete_data_menu(engine)
            else:
                print("\nTerima kasih, program dihentikan.")
                break
    
    except KeyboardInterrupt:
        print("\nProgram dihentikan (Ctrl+C). Terima kasih.\n")

    finally:
        engine.dispose()
        print("Koneksi database berhasil ditutup.\n")

if __name__ == "__main__":
    main()
