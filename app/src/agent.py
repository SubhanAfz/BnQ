import requests
import os
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
@tool
def google_search(query):
    """
    Searches using Google Custom JSON Search API and returns a formatted string of the results, and each result could contain the following:
    - Title (If there is no title it will show "No title" instead)
    - Snippet (If there is no snippet it will show "No snippet" instead)
    - Link (If there is no link it will show "No link" instead)
    If no results are found, it returns "No results found"
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q' : query,
        'key' : os.environ['GOOGLE_API_KEY'],
        'cx': os.environ['GOOGLE_SEARCH_ENGINE_ID']
    }
    response = requests.get(url, params=params)
    data =response.json()
    if "items" in data:
        results=[]
        for item in data["items"]:
            title = item.get("title", "No title")
            snippet = item.get("snippet", "No snippet")
            link = item.get("link", "No link")
            results.append(f"Title: {title}\n Snippet: {snippet}\n Link: {link}\n")
        return "\n".join(results)
    else:
        return "No results found"
@tool
def get_content_of_url(url):
    """
    Get the content of a webpage by sending a GET request to the URL and returning the text content of the page.
    It will remove any unnecessary HTML tags such as script and style tags.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)




tools = [google_search, get_content_of_url]
graph = create_react_agent(model, tools=tools)

    