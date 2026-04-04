from src.agents.scientist.tools import search_arxiv_literature

def test_arxiv_tool():
    """
    Tests the scientist node directly.
    """
    print("\n🔍 Pinging the real arXiv API...")

    result = search_arxiv_literature.invoke({"query":"Vision Transformers for Anomaly Detection"})

    print("\n📥 REAL ARXIV RESULTS:\n")
    print(result)
    
    # Basic assertions to ensure our urllib and XML parsing didn't fail
    assert "Title:" in result
    assert "ERROR" not in result