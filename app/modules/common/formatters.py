"""
Shared formatters and utilities for all domain agents.
"""

def format_as_mermaid(data: str) -> str:
    """Utility to wrap data in a mermaid block if needed."""
    return f"```mermaid\n{data}\n```"
