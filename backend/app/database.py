import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# On Vercel or read-only serverless filesystems, write SQLite database to /tmp
VERCEL_ENV = os.environ.get("VERCEL", "0")
if VERCEL_ENV == "1" or not os.access(os.path.dirname(__file__), os.W_OK):
    DB_PATH = os.path.join(tempfile.gettempdir(), "payguard.db")
else:
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "payguard.db"))

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_tables_created = False

def init_db():
    global _tables_created
    if not _tables_created:
        try:
            import backend.app.models  # noqa: F401
            Base.metadata.create_all(bind=engine)
            _tables_created = True
        except Exception as e:
            print(f"[Database] WARNING: init_db table creation: {e}")

def get_db():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
