# Analytics Engineering: SQL & dbt (Sales Analytics Mart)

Praktikum Analytics Engineering untuk mata kuliah Data Processing Workflow, Politeknik Elektronika Negeri Surabaya (PENS).
Membangun model dimensional (star schema) dari data penjualan retail menggunakan **dbt Core + DuckDB**, lengkap dengan
incremental model, automated testing, dokumentasi, dan lineage.

## Studi kasus

Data operasional: `customers`, `products`, `orders`, `payments`.
Pertanyaan bisnis: *berapa total penjualan per bulan, customer segment, region, dan product category?*

## Arsitektur

```
raw (schema DuckDB)  ->  staging (view)  ->  intermediate (view)  ->  marts (table)
```

| Layer | Folder | Model |
|---|---|---|
| Raw | schema `raw` (dimuat `scripts/bootstrap_raw.sql`) | customers, products, orders, payments |
| Staging | `dbt_project/models/staging/` | `stg_customers`, `stg_products`, `stg_orders`, `stg_payments` |
| Intermediate | `dbt_project/models/intermediate/` | `int_sales` |
| Marts | `dbt_project/models/marts/` | `dim_customer`, `dim_product`, `dim_date`, `fct_sales`, `fct_sales_incremental`, `sales_mart` |

**Grain** `fct_sales`: 1 baris per order line.
**Skema**: Star (kategori dan department berada di `dim_product`).

## Struktur repo

```
.
├── data/                  # 5 file CSV (customers, products, orders, payments, orders_incremental)
├── dbt_project/           # project dbt (jalankan semua perintah dbt dari sini)
│   ├── dbt_project.yml
│   ├── packages.yml
│   ├── profiles.yml.example
│   └── models/            # staging, intermediate, marts, schema.yml
├── scripts/
│   ├── bootstrap_raw.sql  # memuat CSV ke schema raw
│   └── q.py               # helper menjalankan SQL ke DuckDB/SQLite
├── analytics_validation.sqlite
└── SQL_VALIDATION_REPORT.txt
```

## Cara menjalankan (Windows PowerShell)

Prasyarat: Python 3.10+ dan Git.
Jalankan dari **root repo**, dan simpan repo di path yang pendek (hindari batas path 260 karakter Windows).

```powershell
# 1. Virtual environment + dbt
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install dbt-duckdb

# 2. Profile dbt
Copy-Item dbt_project\profiles.yml.example dbt_project\profiles.yml

# 3. Muat data raw ke DuckDB (membuat analytics.duckdb di root)
python scripts\q.py -f scripts\bootstrap_raw.sql
python scripts\q.py "SELECT (SELECT COUNT(*) FROM raw.customers) c, (SELECT COUNT(*) FROM raw.products) p, (SELECT COUNT(*) FROM raw.orders) o, (SELECT COUNT(*) FROM raw.payments) pay"
# expected: (50, 30, 500, 500)

# 4. Build model + test (dari folder dbt_project)
cd dbt_project
dbt debug
dbt build
```

Validasi (data 500 baris): `fct_sales` = 500 baris, quantity 1549, total sales 219137.5, dan total `sales_mart` sama dengan fact.

### Dokumentasi dan lineage

```powershell
dbt docs generate
dbt docs serve    # buka http://localhost:8080, klik ikon graph untuk lineage
```

### Simulasi incremental (+50 order)

```powershell
cd ..
python scripts\q.py "INSERT INTO raw.orders SELECT * FROM read_csv_auto('../data/orders_incremental.csv', HEADER=TRUE)"
cd dbt_project
dbt run --select fct_sales_incremental
```

Jalankan INSERT **sekali saja**. Untuk reset: ulangi `bootstrap_raw.sql`, lalu `dbt run --full-refresh`.

## Testing

`unique`, `not_null`, dan `relationships` pada dimension dan fact (didefinisikan di `models/schema.yml`). Jalankan dengan `dbt test`.

## Catatan

- `analytics.duckdb`, `.venv/`, `target/`, `logs/`, dan `profiles.yml` tidak ikut di-push (lihat `.gitignore`); semuanya dibuat ulang lewat langkah di atas.
- Path di `bootstrap_raw.sql` bersifat relatif (`../data/...`) karena `q.py` menjalankan SQL dari folder `dbt_project/`.
- Strategi incremental memakai `unique_key='order_id'` dan watermark `MAX(order_date)`. Itu sengaja sederhana untuk pembelajaran; data yang terlambat masuk tidak tertangkap (produksi: ingestion timestamp, lookback window, atau CDC).
