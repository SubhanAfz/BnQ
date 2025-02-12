import requests
import os
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from datetime import datetime
from urllib.parse import urlparse, urljoin
from botinstance import bot
import re

#model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

"""
    Non-Discord agentic tools
"""
@tool
def google_search(query: str) -> str:
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
        'key' : os.environ['GOOGLE_SEARCH_API_KEY'],
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
def get_content_of_url(url: str) -> str:
    """
    Get the content of a webpage by sending a GET request to the URL and returning
    the text content of the page in Markdown format. Anchor tags are converted into
    Markdown links, and script/style tags are removed.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    for a in soup.find_all("a", href=True):
        link_text = a.get_text(strip=True) or a["href"]
        href = a["href"]

        parsed_href = urlparse(href)
        full_url = None
        if parsed_href.netloc:
            full_url = href
        else:
            full_url = urljoin(url, href)

        markdown_link = f"[{link_text}]({full_url})"
        a.replace_with(markdown_link)
    
    markdown_text = soup.get_text(separator="\n", strip=True)
    return markdown_text


@tool
def get_date_and_time() -> str:
    """
    Get the current weekday, date and time in the format "Weekday DD-MM-YY HH:MM:SS (Time is in 24hr format)"
    """
    return datetime.now().strftime("%A %d-%m-%Y %H:%M:%S")

"""
    Discord agentic tools
"""
@tool
async def get_discord_user(mention: str) -> str:
    """
    Get the username, display name, ID of a Discord user and if they are a bot from a mention (A mention is <@USERID>).

    The user ID can be found inbetween the <@ and > symbols when a user is mentioned in a message
    """
    user_id_str = re.sub(r"[<@!>]", "", mention)
    user_id = int(user_id_str)
    user = await bot.fetch_user(user_id)
    output = f"Username: {user.name}, Display name: {user.display_name}, ID: {user.id}, IsBot: {user.bot}"
    return output

@tool
def get_discord_guild_info(guild_id: str) -> str:
    """
        Gets the guild ID, the Guild name of a Guild and all the members/users in the Guild.
        When it displays all the members/users in the guild this is the information that is displayed:
            Username, Nickname, Display name, User ID, If they are a bot or not.
        A guild is also known as a Discord Server.
    """
    id= int(guild_id)
    guild = bot.get_guild(id)
    if guild:
        output = f"""Guild: {guild.id}, Guild name: {guild.name}
Members (Length of Member list: {len(guild.members)}):
"""
        for member in guild.members:
                output += f"\n Member/User username: {member.name}, Member/User nickname: {member.nick}, Member/User display name: {member.display_name}, Member/User ID: {member.id}, Member/User is a bot: {member.bot}"
        return output
    else:
        return "Couldn't find Guild!"



tools = [google_search, get_content_of_url, get_date_and_time, get_discord_user, get_discord_guild_info]
graph = create_react_agent(model, tools=tools)

    