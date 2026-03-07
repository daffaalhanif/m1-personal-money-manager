import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from datetime import datetime

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



# === Membuat 'SQLAlchemy Engine' dari Konfigurasi di File .env -> (Return: Engine)===
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
        print("Engine database berhasil dibuat.\n")
        return engine
    
    except Exception as e:
        print("Gagal membuat engine database.")
        print(f"Detail error: '{e}'")
        return None

# === Input 'ANGKA' Aman Agar Program Tidak Crash Jika User Salah Input -> (Return: Angka INT) ===
def safe_int_input(prompt, pilihan_valid=None):
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

# === Input 'TANGGAL' Aman dengan Format YYYY-MM-DD -> (Return: String Tanggal yang Valid) ===
def safe_date_input(prompt):
    while True:
        date_str = input(prompt).strip()

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            return parsed_date
        
        except ValueError:
            print("Format tanggal harus YYYY-MM-DD. Contoh: 2026-12-01\n")

# === Input 'AMOUNT' Aman (Boleh INT / FLOAT) dengan Syarat > 0 -> (Return: Amount FLOAT) ===
def safe_amount_input(prompt):
    while True:
        amount_str = input(prompt).strip()

        if amount_str == "":
            print("Input tidak boleh kosong.\n")
            continue
        
        try:
            amount = float(amount_str)
        except ValueError:
            print("Amount harus berupa angka. Contoh: 50000 atau 50000.75\n")
            continue

        if amount <= 0:
            print("Amount harus lebih dari 0.\n")
            continue

        return amount

# === Input 'FLOW' Aman dengan Pilihan Valid -> (Return: "IN" / "OUT")
def safe_flow_input(prompt="Masukkan flow (IN/OUT): "):
    while True:
        flow = input(prompt).strip().upper()

        if flow == "":
            print("Input tidak boleh kosong.\n")
            continue

        if flow in ("IN", "OUT"):
            return flow
        
        print('Flow harus "IN" / "OUT".\n')

# === Menjalankan Query 'SELECT' -> (Return: DataFrame) ===
def run_select_df(engine, query, params=None):
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
    
# === Menjalankan Query 'Non-SELECT' (INSERT / UPDATE) -> (Return: True / False) ===
def run_execute(engine, query, params=None):
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

# === Menampilkan 'DATAFRAME' -> (Return: DataFrame) ===
def show_dataframe(df):
    if df.empty:
        print("(Data kosong / tidak ada baris.)\n")
        return
    
    print(df.to_string(index=False))
    print("")

# ===========================================================
#                    FEATURE 1: SHOW TABLE
# ===========================================================

# === Menampilkan Tabel CATEGORIES ===
def show_categories(engine, flow=None):
    if flow is None:
        print("\n---- TABLE CATEGORIES (ALL) ----")
        query = """
            SELECT category_id, category_name, flow
            FROM categories
            ORDER BY category_id
        """
        df = run_select_df(engine, query)
        show_dataframe(df)
        return df
    
    flow = flow.upper().strip()

    print(f"\n----- TABLE CATEGORIES {flow} -----")
    query = """
        SELECT category_id, category_name, flow
        FROM categories
        WHERE flow = :flow
        ORDER BY category_id
    """
    df = run_select_df(engine, query, params={"flow": flow})
    show_dataframe(df)
    return df

# === Menampilkan Tabel TRANSACTIONS (JOIN category_name) dengan Default LIMIT: 20 ===
def show_transactions_view_all(engine, limit=20):
    print(f"\n-------------------- TABLE TRANSACTIONS (VIEW ALL - LIMIT {limit}) -------------------")
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
    show_dataframe(df)

# === Menampilkan Table TRANSACTIONS by FLOW (IN / OUT) dengan Default LIMIT: 20 ===
def show_transactions_filter_flow(engine, flow, limit=20):
    flow = flow.upper().strip()

    if flow not in ("IN", "OUT"):
        print('Flow harus "IN" atau "OUT".\n')
        return
    
    print(f"\n------------------ TABLE TRANSACTIONS (FLOW {flow} - LIMIT {limit}) --------------------")
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
    show_dataframe(df)

# ========== OPSI MENU 1: SHOW TABLE ==========
def show_table_menu(engine):
    while True:
        print("\n=== Menu 1: SHOW TABLE ===")
        print("1. Table Categories")
        print("2. Table Transactions")
        print("3. Back\n")

        choice = safe_int_input("Pilih menu (1-3): ", range(1,4))

        if choice == 1:
            while True:
                print("\n--- Sub-Menu 1: TABLE CATEGORIES ---")
                print("1. View ALL Categories")
                print("2. View IN Categories")
                print("3. View OUT Categories")
                print("4. Back\n")

                sub = safe_int_input("Piih menu (1-4): ", range(1, 5))

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
                print("\n------ Sub-Menu 2: TABLE TRANSACTIONS ------")
                print("1. View All Transactions (Default limit: 20)")
                print("2. Filter by Flow (IN / OUT)")
                print("3. Back\n")

                sub = safe_int_input("Pilih menu (1-3): ", range(1, 4))

                if sub == 1:
                    show_transactions_view_all(engine)
                elif sub == 2:
                    flow = safe_flow_input("\nMasukkan flow (IN / OUT): ")
                    show_transactions_filter_flow(engine, flow)
                else:
                    break

        else:
            return

# ===========================================================
#                   FEATURE 2: SHOW STATISTIK
# ===========================================================

# === Menampilkan Basic STATISTIK (COUNT, SUM, AVG) by FLOW (ALL / IN / OUT) ===
def get_basic_stats(engine, flow=None):
    """
    flow:
    - "None" -> ALL
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

    total_trx = df.loc[0, "total_transaksi"] or 0
    total_amount = df.loc[0, "total_amount"] or 0
    avg_amount = df.loc[0, "avg_amount"] or 0

    return total_trx, total_amount, avg_amount

# === Menampilkan DATAFRAME STATISTIK per KATEGORI by FLOW (IN / OUT) ===
def show_stats_per_category_by_flow(engine, flow):
    flow = flow.upper().strip()

    if flow not in ("IN", "OUT"):
        print("Flow harus IN atau OUT.\n")
        return

    print(f"\n----------- STATISTIK PER KATEGORI ({flow}) ----------")

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
        print("(Tidak ada data OUT untuk dihitung.)\n")
        return
    
    print(df.to_string(index=False))
    print("")

# ========== OPSI MENU 2: SHOW STATISTIK ==========
def show_statistik_menu(engine):
    while True:
        print("\n===== Menu 2: SHOW STATISTIK =====")
        print("1. Statistik ALL (COUNT, SUM, AVG)")
        print("2. Statistik IN (COUNT, SUM, AVG)")
        print("3. Statistik OUT (COUNT, SUM, AVG)")
        print("4. Statistik per Kategori (IN)")
        print("5. Statistik per Kategori (OUT)")
        print("6. Back\n")

        choice = safe_int_input("Pilih menu (1-6): ", range(1,7))
        
        if choice == 1:
            total_trx, total_amount, avg_amount = get_basic_stats(engine, flow=None)
            print("\n-------- STATISTIK ALL --------")
            print(f"Total Transaksi : {total_trx}")
            print(f"Total Amount    : {total_amount}")
            print(f"Average Amount  : {avg_amount}")

        elif choice == 2:
            total_trx, total_amount, avg_amount = get_basic_stats(engine, flow="IN")
            print("\n-------- STATISTIK IN --------")
            print(f"Total Transaksi : {total_trx}")
            print(f"Total Amount    : {total_amount}")
            print(f"Average Amount  : {avg_amount}")

        elif choice == 3:
            total_trx, total_amount, avg_amount = get_basic_stats(engine, flow="OUT")
            print("\n-------- STATISTIK OUT --------")
            print(f"Total Transaksi : {total_trx}")
            print(f"Total Amount    : {total_amount}")
            print(f"Average Amount  : {avg_amount}")

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
def plot_histogram_amount(engine):
    query = """
        SELECT amount
        FROM transactions
    """
    df = run_select_df(engine, query)

    if df.empty:
        print("(Data transactions kosong, histogram tidak dapat ditampilkan.)\n")
        return

    plt.figure()
    sns.histplot(data=df, x="amount", bins=15)

    plt.title("Histogram Amount (Semua Transaksi)")
    plt.xlabel("Amount")
    plt.ylabel("Frekuensi")

    plt.ticklabel_format(style='plain', axis='x')

    plt.tight_layout()
    plt.show()
    plt.close()

# === Menampilkan 'BAR PLOT' Top 5 KATEGORI OUT Berdasarkan TOTAL AMOUNT (SUM) ===
def plot_top5_out_categories(engine):
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
        print("(Tidak ada data OUT untuk ditampilkan.)\n")
        return
    
    plt.figure()
    sns.barplot(data=df, x="total_out", y="category_name")

    plt.title("Top 5 OUT Categories (Total Amount)")
    plt.xlabel("Total OUT (SUM Amount)")
    plt.ylabel("Category")

    plt.ticklabel_format(style='plain', axis='x')

    plt.tight_layout()
    plt.show()
    plt.close()

# ========== OPSI MENU 3: DATA VISUALIZATION ==========
def show_visualization_menu(engine):
    while True:
        print("\n=== Menu 3: Data Visualization ===")
        print("1. Histogram Amount")
        print("2. Top 5 OUT Categories")
        print("3. Back\n")

        choice = safe_int_input("Pilih menu (1-3): ", range(1,4))

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
def add_transaction(engine):
    """
    Flow:
    1) Input trx_date
    2) Input amount
    3) Input flow (IN / OUT)
    4) Pilih category_id (Tampilkan categories dulu)
    5) Input note (Opsional. Boleh kosong)
    6) INSERT ke table transactions
    """
    print("\n---------- ADD TRANSACTION ----------")

    trx_date = safe_date_input("Masukkan trx_date (YYYY-MM-DD): ")
    amount = safe_amount_input("Masukkan amount (> 0): ")
    flow = safe_flow_input("Masukkan flow transaksi (IN/OUT): ")

    print("\nDaftar Categories (Sesuai flow transaksi):")
    df_cat = show_categories(engine, flow=flow)
    if df_cat.empty:
        print(f"(Tidak ada kategori flow {flow}. Tambahkan category dulu.)\n")
        return
    
    valid_ids = set(df_cat["category_id"])

    while True:
        category_id = safe_int_input(f"\nPilih category_id dari Tabel Categories {flow} (0=Back, 9=Ganti Flow): ")

        if category_id == 0:
            print("\nInput transaksi dibatalkan.")
            return
        
        if category_id == 9:
            flow = safe_flow_input("\nMasukkan flow transaksi (IN/OUT): ")

            print("\nDaftar Categories (Sesuai flow transaksi):")
            df_cat = show_categories(engine, flow=flow)
            if df_cat.empty:
                print(f"(Tidak ada kategori flow {flow}. Tambahkan kategori dulu.)\n")
                return
            
            valid_ids = set(df_cat["category_id"])
            continue

        if category_id in valid_ids:
            break

        print("category_id tidak sesuai flow transaksi. Pilih dari daftar.")

    note = input("Masukkan note (Opsional): ").strip()
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
        print("\nTransaction added successfully.\n")

# === ADD DATA New Category ke Tabel CATEGORIES ===
def add_category(engine):
    """
    Flow:
    1) Show tabel categories (ALL)
    2) Input nama category baru
    3) Validasi tidak boleh kosong
    4) Flow wajib IN atau OUT
    5) Handle duplicate (UNIQUE category_name)
    6) INSERT ke table categories
    """
    print("\n---------- ADD CATEGORY ----------")
    print("Daftar Categories saat ini:")
    show_categories(engine)

    print("\nSilakan tambah category baru.")

    while True:
        category_name = input("Masukkan category_name: ").strip()
        if category_name != "":
            break
        print("\ncategory_name tidak boleh kosong.\n")

    flow = safe_flow_input("Masukkan flow category (IN/OUT): ")

    query = """
        INSERT INTO categories (category_name, flow)
        VALUES (:category_name, :flow)
    """

    try:
        with engine.begin() as connection:
            connection.execute(text(query), {"category_name": category_name, "flow": flow})
        
        print(f"\nNew Category Added Successfully: {category_name}")
        print("\nDaftar Categories terbaru:")
        show_categories(engine)

    except IntegrityError:
        print("\nCategory sudah ada (Duplicate). Silakan pakai nama lain.\n")

    except Exception as e:
        print("\nGagal menambahkan category.")
        print(f"Detail error: {e}\n")

# ========== OPSI MENU 4: ADD DATA ==========
def add_data_menu(engine):
    while True:
        print("\n=== Menu 4: ADD DATA ===")
        print("1. Add Transaction")
        print("2. Add Category")
        print("3. Back\n")

        choice = safe_int_input("Pilih menu (1-3): ", range(1,4))

        if choice == 1:
            add_transaction(engine)
        elif choice == 2:
            add_category(engine)
        else:
            return

# ===========================================================
#                      MAIN PROGRAM MENU
# ===========================================================

def main():
    print("\n======= Xpense Insight =======")

    engine = create_engine_from_env()
    if engine is None:
        print("\nProgram berhenti karena tidak bisa connect ke database.")
        return
    
    try:
        while True:
            print("\n====== MAIN MENU ======")
            print("1. Show Table")
            print("2. Show Statistik")
            print("3. Data Visualization")
            print("4. Add Data")
            print("0. Exit")
            print("=======================\n")

            choice = safe_int_input("Pilih menu (0-4): ", range(5))

            if choice == 1:
                show_table_menu(engine)
            elif choice == 2:
                show_statistik_menu(engine)
            elif choice == 3:
                show_visualization_menu(engine)
            elif choice == 4:
                add_data_menu(engine)
            else:
                print("\nTerima kasih, program dihentikan.")
                break
    
    except KeyboardInterrupt:
        print("\nProgram dihentikan (Ctrl+C). Terima kasih.\n")

    finally:
        engine.dispose()
        print("Engine koneksi database berhasil ditutup.")

if __name__ == "__main__":
    main()
