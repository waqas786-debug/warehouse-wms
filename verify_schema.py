from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    tables = sorted(db.metadata.tables.keys())
    print("\n" + "="*50)
    print(f" TOTAL REGISTERED DATABASE TABLES: {len(tables)} ")
    print("="*50)
    for idx, table in enumerate(tables, 1):
        print(f"{idx:02d}. {table}")
    print("="*50)
    if len(tables) >= 40:
        print(" SUCCESS: Academic requirement of >= 40 tables satisfied!")
    else:
        print(f" WARNING: Only {len(tables)} tables registered.")
    print("="*50 + "\n")
