import requests
import openai
from bs4 import BeautifulSoup
import time

# Set up Google Search API
GOOGLE_SEARCH_API_KEY = "AIzaSyCW4tazGbiz_vo"
GOOGLE_SEARCH_ENGINE_ID = "94c0fff8c"

# Set up OpenAI API

OPENAI_API_KEY = "sk-"
openai.api_key = OPENAI_API_KEY

# List of sources to search from
SOURCES = ['Yahoo Finance']

# List of queries to search for
QUERIES = ['foreign exchange market news', 'Euro United States dollar news']

def get_google_search_results(query, source):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': GOOGLE_SEARCH_API_KEY,
        'cx': GOOGLE_SEARCH_ENGINE_ID,
        'q': query + " site:" + source,
        'num': 5,
        'safe': 'active',
        'fields': 'items(title,link,snippet)'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('items', [])

def scrape_full_article(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    article_text = "\n".join([p.get_text() for p in paragraphs])
    return article_text

def generate_gpt3_response(prompt, search_results):
    search_results_str = "\n".join([
        f"Title: {result['title']}\nLink: {result['link']}\nArticle: {scrape_full_article(result['link'])}" 
        for result in search_results
    ])
    prompt_with_results = f"{prompt}. The search results are:\n{search_results_str}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are News GPT, a model specializing in analyzing news articles related to the foreign exchange market."},
            {"role": "user", "content": prompt_with_results}
        ],
        max_tokens=16000
    )
    return response.choices[0].message.content.strip()

while True:
    for source in SOURCES:
        for query in QUERIES:
            search_results = get_google_search_results(query, source)
            gpt3_response = generate_gpt3_response(f"Search the web for '{query}' on {source}", search_results)
            print(f"From {source}:\n{gpt3_response}\n")
    time.sleep(3600)  # sleep for an hour before searching again
