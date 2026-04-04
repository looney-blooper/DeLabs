from langchain_core.tools import tool

import urllib.parse
import xml.etree.ElementTree as ET

@tool
def search_arxiv_literature(query : str) -> str:
    """
    Use this tool to search the arXiv database for recent deep learning research papers.
    Pass a highly specific search query (e.g: 'Hyperspectral Image Anomaly Detection').
    """
    try:
        search_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results=3"

        response = urllib.request.urlopen(url)
        xml_data = response.read()
        root = ET.fromstring(xml_data)

        ns = {'arxiv' : 'http://www.w3.org/2005/Atom'}
        results = []

        for entry in root.findall('arxiv:entry', ns):
            title = entry.find('arxiv:title', ns).text.replace('\n', ' ')
            summary = entry.find('arxiv:summary',ns).text.replace('\n', ' ')
            results.append(f"Title: {title}\nSummary: {summary[:300]}...\n")

        if not results:
            return f"No arXiv results found for '{query}'. Try a broader search term."

        return "\n---\n".join(results)
    
    except Exception as e:
        return f"ERROR: arXiv API search failed: {str(e)}"



scientist_tools = [search_arxiv_literature]
