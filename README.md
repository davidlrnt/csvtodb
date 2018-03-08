# CSV TO DB

Python CSV reader and db insert


### Prerequisites


```
psycopg2
```

### Usage

Edit .env file to include db credentials
Caution! - If using git add .env to .gitignore

Csv must include headers that match table column names


```
python csvtodb.py FILE.CSV TABLENAME
```
