"""
Database connection management for PostgreSQL with pgvector.

Provides connection pooling and configuration loading from environment variables.
"""

import logging
import os
from pathlib import Path
from typing import Optional

import psycopg2
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)


def get_connection():
    """
    Get a PostgreSQL connection to the astronomy_rag_corpus database.

    Loads connection parameters from environment variables:
    - PGSQL01_HOST: Database host
    - PGSQL01_ADMIN_USER: Database username
    - PGSQL01_ADMIN_PASSWORD: Database password
    - PGSQL01_RAG_CORPUS_DB: Database name (default: astronomy_rag_corpus)

    Returns:
        psycopg2 connection object

    Raises:
        KeyError: If required environment variables are missing
        psycopg2.OperationalError: If connection fails
    """
    # AI NOTE: Connection parameters are loaded from environment variables to
    # avoid hardcoding credentials. The env file location is detected
    # automatically by dotenv.find_dotenv() which checks common paths including
    # D:\development-repositories\.global-env\.env on Windows.

    # Load environment variables
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        logger.debug(f"Loading environment from: {dotenv_path}")
        load_dotenv(dotenv_path)

    # Get connection parameters from environment
    host = os.getenv("PGSQL01_HOST")
    user = os.getenv("PGSQL01_ADMIN_USER")
    password = os.getenv("PGSQL01_ADMIN_PASSWORD")
    database = os.getenv("PGSQL01_RAG_CORPUS_DB", "astronomy_rag_corpus")

    # Validate required parameters
    if not host:
        raise KeyError("PGSQL01_HOST environment variable is required")
    if not user:
        raise KeyError("PGSQL01_ADMIN_USER environment variable is required")
    if not password:
        raise KeyError("PGSQL01_ADMIN_PASSWORD environment variable is required")

    logger.info(f"Connecting to PostgreSQL database '{database}' on host '{host}'")

    # Create connection
    try:
        conn = psycopg2.connect(
            host=host,
            port=5432,
            user=user,
            password=password,
            database=database,
            connect_timeout=10,
        )

        logger.info(f"Successfully connected to database '{database}'")

        return conn

    except psycopg2.OperationalError as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def test_connection() -> bool:
    """
    Test database connection without keeping it open.

    Returns:
        True if connection succeeds, False otherwise
    """
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False
