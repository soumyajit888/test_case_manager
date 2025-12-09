# backend/config.py

import os

class Config:
    """
    Application configuration settings, loaded primarily from environment variables.
    This centralized configuration makes the application highly customizable and secure.
    """
    
    # --- PostgreSQL Database Configuration ---
    # These variables are read by db_connector.py
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'ldqa_checklist')
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    
    # --- External Service Links ---
    # Base URL for JIRA issues (used by the frontend and the JIRA simulation endpoint)
    JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://yourcompany.atlassian.net/browse/')
    
    # --- API Keys (Placeholder) ---
    JIRA_API_KEY = os.environ.get('JIRA_API_KEY', 'YOUR_JIRA_API_KEY_PLACEHOLDER')
    
    # --- FastAPI Server Configuration ---
    FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', '*')
