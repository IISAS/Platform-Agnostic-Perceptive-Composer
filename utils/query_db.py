import os

import polars as pl

DB_URI: str = "postgresql://{user}:{password}@{host}:{port}/{name}".format(
    user=os.environ.get("DOMINO_DB_USER", "postgres"),
    password=os.environ.get("DOMINO_DB_PASSWORD", "postgres"),
    host=os.environ.get("DOMINO_DB_HOST", "domino-postgres"),
    port=os.environ.get("DOMINO_DB_PORT", "5432"),
    name=os.environ.get("DOMINO_DB_NAME", "postgres"),
)


def get_pieces_info():
    uri = DB_URI
    query = "SELECT * FROM piece"

    df = pl.read_database_uri(query=query, uri=uri)
    df = df.with_columns(('["' + pl.col("tags").list.join('", "') + '"]').alias("tags"))

    df = df.filter(pl.col("name") != "ImageFilterPiece")

    return df.select("id", "name", "description", "tags", "input_schema", "output_schema")


def get_pieces_full_info() -> dict:
    """Return all piece metadata keyed by piece ID."""
    uri = DB_URI
    piece_query = "SELECT * FROM piece"
    piece_repository_query = "SELECT * FROM piece_repository"
    
    piece_df = pl.read_database_uri(query=piece_query, uri=uri)
    piece_repository_df = pl.read_database_uri(query=piece_repository_query, uri=uri)
    piece_repository_df = piece_repository_df.select(pl.all().name.prefix("repository_"))

    piece_df = piece_df.join(piece_repository_df, on='repository_id')

    result = {}
    for row in piece_df.to_dicts():
        piece_id = row.get("id")
        if piece_id is not None:
            result[piece_id] = row
    return result
