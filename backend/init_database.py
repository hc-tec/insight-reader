#!/usr/bin/env python3
"""
Database initialization script

Usage:
    python init_database.py

This script creates all database tables defined in the models.
Run this after setting up your PostgreSQL database for the first time.
"""

import sys
from app.db.database import init_db
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def main():
    """Initialize database tables"""
    logger.info("=" * 60)
    logger.info("Database Initialization Script")
    logger.info("=" * 60)

    logger.info(f"\nDatabase URL: {settings.database_url}")

    if "postgresql" in settings.database_url:
        logger.info("Database Type: PostgreSQL")
    else:
        logger.info("Database Type: SQLite")

    logger.info("\nInitializing database tables...")

    try:
        init_db()
        logger.info("\n[SUCCESS] Database tables created successfully!")
        logger.info("\nCreated tables:")
        logger.info("  - users")
        logger.info("  - articles")
        logger.info("  - insights")
        logger.info("  - collections")
        logger.info("  - sparks")
        logger.info("  - meta_analysis")
        logger.info("  - thinking_lens")
        logger.info("  - insight_history")
        logger.info("  - preferences")
        logger.info("\n" + "=" * 60)
        return 0

    except Exception as e:
        logger.error(f"\n[ERROR] Failed to initialize database")
        logger.error(f"Error details: {str(e)}")
        logger.error("\nPlease check:")
        logger.error("  1. Database connection string is correct")
        logger.error("  2. Database server is running")
        logger.error("  3. Database user has proper permissions")
        logger.error("  4. Database exists")
        logger.error("\n" + "=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
