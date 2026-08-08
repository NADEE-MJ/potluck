"""Database connection and session management."""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Database URL from settings
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Additive-only migrations: (table, column, DDL type/default clause).
# This app has no migration framework (see CLAUDE.md), and
# Base.metadata.create_all() only creates missing *tables* - it never adds
# columns to a table that already exists. Any new nullable/defaulted column
# added to a model needs an entry here so it lands on a DB that predates it,
# instead of requiring everyone to manually run SQL or drop the file.
_COLUMN_MIGRATIONS = [
    ("items", "display_order", "INTEGER DEFAULT 0"),
]


def run_migrations():
    """Add any columns from _COLUMN_MIGRATIONS that don't exist yet.

    Safe to run on every startup: each column is only added if missing, so
    an already-migrated DB is untouched (no-op), and a table that doesn't
    exist yet is skipped here (create_all() below creates it fresh, with
    every current column already present).
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        for table, column, ddl in _COLUMN_MIGRATIONS:
            if table not in existing_tables:
                continue
            existing_columns = {col["name"] for col in inspector.get_columns(table)}
            if column not in existing_columns:
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
                print(f"Migration: added column {table}.{column}")


def _backfill_uniform_display_order(connection, table, group_column):
    """Give each row in `table` a distinct display_order (by id, within its
    group_column) whenever its whole sibling group currently shares one
    identical value.

    Categories/items created before display_order was wired up (or added
    by this migration with a DEFAULT) all land on the same value, which
    breaks move-up/move-down: it compares by strict </> so a group tied at
    the same number has no "next" sibling to swap with. Renumbering only
    when a group is *uniform* makes this safe to run on every startup: the
    first move on a group differentiates its values, so later runs leave
    it alone instead of clobbering someone's chosen order.
    """
    groups = connection.execute(
        text(f"SELECT DISTINCT {group_column} FROM {table}")
    ).fetchall()

    for (group_id,) in groups:
        rows = connection.execute(
            text(
                f"SELECT id, display_order FROM {table} "
                f"WHERE {group_column} = :group_id ORDER BY id"
            ),
            {"group_id": group_id},
        ).fetchall()

        if len(rows) < 2:
            continue
        distinct_orders = {row[1] for row in rows}
        if len(distinct_orders) > 1:
            continue  # already differentiated - leave it alone

        for position, (row_id, _) in enumerate(rows):
            connection.execute(
                text(f"UPDATE {table} SET display_order = :order WHERE id = :id"),
                {"order": position, "id": row_id},
            )


def backfill_display_order():
    """Renumber categories/items whose sibling group is still uniformly
    ordered, so move-up/move-down has something to swap with. See
    _backfill_uniform_display_order for why this is safe to call every
    startup."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        if "categories" in existing_tables:
            _backfill_uniform_display_order(connection, "categories", "potluck_id")
        if "items" in existing_tables:
            _backfill_uniform_display_order(connection, "items", "category_id")


def init_db():
    """Initialize database tables."""
    from app import models  # Import models to register them
    run_migrations()
    Base.metadata.create_all(bind=engine)
    backfill_display_order()


def get_db():
    """
    Dependency for routes to get database session.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
