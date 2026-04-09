import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DeLabs Literature Server")

@mcp.tool()
def search_arxiv_literature(query: str) -> str:
    """Searches the arXiv database for recent deep learning papers."""
    try:
        search_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results=3"
        
        response = urllib.request.urlopen(url)
        xml_data = response.read()
        root = ET.fromstring(xml_data)

        ns = {'arxiv': 'http://www.w3.org/2005/Atom'}
        results = []
        for entry in root.findall('arxiv:entry', ns):
            title = entry.find('arxiv:title', ns).text.replace('\n', ' ')
            summary = entry.find('arxiv:summary', ns).text.replace('\n', ' ')
            results.append(f"Title: {title}\nSummary: {summary[:300]}...\n")

        if not results:
            return f"No arXiv results found for '{query}'."
        return "\n---\n".join(results)
    except Exception as e:
        return f"ERROR: arXiv API search failed: {str(e)}"

if __name__ == "__main__":
    mcp.run()