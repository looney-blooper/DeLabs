from langchain_core.tools import tool

@tool
def search_arxiv_literature(query : str) -> str:
    """
    Use this tool to search the arXiv database for recent deep learning research papers.
    Pass a highly specific search query (e.g: 'Hyperspectral Image Anomaly Detection').
    """

    return f"MOCK ARXIV RESULT for '{query}': Recent papers suggest using a Graph-based Vision Transformer with a Gated mechanism for optimal feature extraction."

scientist_tools = [search_arxiv_literature]
