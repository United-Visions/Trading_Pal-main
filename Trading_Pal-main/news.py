import requests
import openai

# Set up Google Search API
GOOGLE_SEARCH_API_KEY = "AIzaSyCWbiz_vo"
GOOGLE_SEARCH_ENGINE_ID = "94c0f38c"

# Set up OpenAI API
OPENAI_API_KEY = "D9R"
openai.api_key = OPENAI_API_KEY

def get_google_search_results(query):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': GOOGLE_SEARCH_API_KEY,
        'cx': GOOGLE_SEARCH_ENGINE_ID,
        'q': query,
        'num': 5,
        'safe': 'active',
        'fields': 'items(title,link,snippet)'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('items', [])

def generate_gpt3_response(prompt, search_results):
    search_results_str = "\n".join([f"Title: {result['title']}\nLink: {result['link']}\nSnippet: {result['snippet']}" for result in search_results])
    prompt_with_results = f"{prompt}. The search results are:\n{search_results_str}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_with_results}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

user_input = input("Enter your query: ")
gpt3_prompt = f"Search the web for '{user_input}'"
search_results = get_google_search_results(user_input)
gpt3_response = generate_gpt3_response(gpt3_prompt, search_results)

print("Response:", gpt3_response)

while True:
    user_feedback = input("Was the response satisfactory? (yes/no): ")
    if user_feedback.lower() == 'yes':
        break

    user_input = input("Please refine your query or ask in a different way: ")
    gpt3_prompt = f"{gpt3_response}. {user_input}"
    search_results = get_google_search_results(user_input)
    gpt3_response = generate_gpt3_response(gpt3_prompt, search_results)

    print("Response:", gpt3_response)