from langchain.tools import tool
import os
from langchain_community.document_loaders import ObsidianLoader


@tool
def get_info_from_vault_tool(query: str) -> str:
    """Tool for retrieving information from a vault.

    Args:
        query (str): The query to search in the vault.
    Returns:
        str: The result of the search in the vault.
    """
    loader = ObsidianLoader(path="C:\\Users\\User\\Desktop\\Games\\My notes")
    results = loader.load()
    return f"Found {len(results)} for '{query}'"
