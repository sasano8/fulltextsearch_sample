# fulltextsearch
fastapi + sqlalchemy + postgressqlで全文検索を実装します。

# getting started

1. プロジェクトルートに`.env`を作成します

```
# OS
TZ=Asia/Tokyo

# POSTGRES
POSTGRES_DB=sample_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
PGTZ=Asia/Tokyo

# APP
DB_HOST=localhost:5432
DB_TEST_HOST=localhost:5435

POSTGRES_TEST_DB=test_sample_db
PGADMIN_LISTEN_PORT=5050
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=yourpassword

```

1. データベースを起動します

``` shell
docker-compose up -d
```

2. データベースを初期化します

``` shell
poetry run python -m fulltextsearch init_db
```

3. アプリケーションを起動します

``` shell
poetry run uvicorn fulltextsearch:app --reload
```

4. 次のURLへアクセスします（OpenAPI Viewerが表示されます）
- GET http://127.0.0.1:8000

5. テストデータをロードします
- POST http://127.0.0.1:8000/system/load_test_data

6. 全文検索します
- GET http://127.0.0.1:8000/heroes?query=山田

7. 後片付け

``` shell
docker-compose down
```

なお、ソースコードを変更すると、アプリケーションが再起動します。
アプリケーション起動時に、自動的にテーブルが初期化されることに注意してください。

# 課題

テストデータに"山田太郎"が含まれています。
しかし、次のクエリを実行した時、1はヒットしますが、2はヒットしません。

1. GET http://127.0.0.1:8000/heroes?query=山
2. GET http://127.0.0.1:8000/heroes?query=郎

そもそも、後方一致が全く効かず、本番では全く使えません。

postgresqlの全文検索はアジア圏の文字を正確に検索できないので、日本語検索の拡張を導入する必要があります。

候補は次の通りです。

- textsearch_ja（mecabによる形態素解析可能）
- pg_bigm（バイグラムによる検索）
- PGroonga(pg_bigmより検索が高速。ただし、pg_bigmよりインデックス作成時間が遅い)

# アプリケーション実装上の注意点

SQLAlchemy-Searchableによって全文検索を実現しています。
要点として、次の手続きを守る必要があります。

1. モデル作成前に`make_searchable`を呼び出す
2. テーブル作成前に`configure_mappers`を呼び出す

``` python
import sqlalchemy as sa
import SQLModel
from sqlalchemy_utils.types import TSVectorType


make_searchable(SQLModel.metadata, options={})

class Person(SqlModel, table=True):
    name: str
    kana: str = ""
    search_vector: Optional[str] = Field(sa_column=Column(TSVectorType(name, kana))

sa.orm.configure_mappers()
```

拡張機能を導入した場合、次のように拡張機能を有効にできます。
（拡張毎に前準備は異なります）

``` python
make_searchable(SQLModel.metadata, options={regconfig="pg_catalog.japanese"})
```
