from google.adk.agents import Agent
from typing import Dict, List
import re

def web_search(query: str, url: str) -> Dict:
    """Searches a specific URL for content related to the query.

    Args:
        query (str): The search query.
        url (str): The URL to search within.

    Returns:
        Dict: A dictionary containing the search status and results.
    """
    try:
        # Simulate web search and content extraction
        if "reuters.com/technology/" not in url:
            return {"status": "error", "result": "Invalid URL. Must be within reuters.com/technology/"}

        # Mock Reuters tech news content
        mock_reuters_content = """
        <h1>Top Tech News</h1>
        <article>
            <h2><a href="#">Tech Company A Announces New AI Chip</a></h2>
            <p>Tech Company A unveiled its latest AI chip, promising significant performance improvements.</p>
        </article>
        <article>
            <h2><a href="#">Cybersecurity Firm Reports Increase in Ransomware Attacks</a></h2>
            <p>A leading cybersecurity firm has reported a surge in ransomware attacks targeting critical infrastructure.</p>
        </article>
        <article>
            <h2><a href="#">New Smartphone Release Faces Supply Chain Issues</a></h2>
            <p>The highly anticipated new smartphone release is facing delays due to ongoing supply chain disruptions.</p>
        </article>
        """

        # Extract relevant snippets based on the query (crude simulation)
        articles = re.findall(r"<article>(.*?)</article>", mock_reuters_content, re.DOTALL)
        relevant_snippets = []
        for article in articles:
            if query.lower() in article.lower():
                relevant_snippets.append(article)

        if not relevant_snippets:
            return {"status": "success", "result": "No relevant articles found."}

        return {"status": "success", "result": relevant_snippets}

    except Exception as e:
        return {"status": "error", "result": str(e)}


def summarise(text: str) -> Dict:
    """Summarizes a given text.

    Args:
        text (str): The text to summarize.

    Returns:
        Dict: A dictionary containing the summarization status and the summarized text.
    """
    try:
        # Simulate summarization
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 2:
            summary = " ".join(sentences[:2]) + "..."  # Take the first two sentences
        else:
            summary = text
        return {"status": "success", "result": summary}
    except Exception as e:
        return {"status": "error", "result": str(e)}


root_agent = Agent(
    name="reuters_tech_news_agent",
    model="gemini-2.0-flash",
    description="Agent that can web search for top tech news on Reuters website and summarise it for user",
    instruction="The agent should visit reuters.com/technology/ and identify top 3-5 tech news articles. For each article, extract the headline and a brief summary. Finally, present the information to the user in a concise format.",
    tools=[web_search, summarise]
)