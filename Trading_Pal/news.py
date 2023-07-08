import os
import openai
import requests
import dotenv
import trafilatura
import gpt_index
from pprint import pprint

import logging
logging.basicConfig(level=logging.DEBUG)

dotenv.load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
bing_search_api_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
bing_search_endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + 'v7.0/search'


def search(query):
    response = requests.get(bing_search_endpoint, headers={
        'Ocp-Apim-Subscription-Key': bing_search_api_key}, params={'q': query, 'mkt': 'en-US'}).json()
    return [result for result in response.get('webPages', {}).get('value', [])]


def add_website_content(result):
    result['content'] = trafilatura.extract(
        trafilatura.fetch_url(url=result['url']))
    return result


def split_content(content, split_length):
    segments = []
    for line in content.split('\n'):
        segments.extend(split_line(line, split_length))
    segments = merge_segments(segments, split_length)
    pprint(len(segments))
    return segments


def split_line(line, split_length):
    words = line.split()
    segments = []
    current_segment = ""
    for i, word in enumerate(words):
        if len(current_segment + " " + word) <= split_length:
            current_segment += (" " if current_segment else "") + word
        else:
            segments.append(current_segment)
            current_segment = word
    if current_segment:
        segments.append(current_segment)
    return segments


def merge_segments(segments, split_length):
    new_segments = []
    current_segment = ""
    for segment in segments:
        if len(current_segment + " " + segment) > split_length and current_segment:
            new_segments.append(current_segment.strip())
            current_segment = segment
        else:
            current_segment += (" " if current_segment else "") + segment
    if current_segment:
        new_segments.append(current_segment.strip())
    return new_segments


def answer_question(question):
    results = search(question)
    results_with_content = [add_website_content(
        result) for result in results[:5]]

    results_with_split_content = [
        {'name': result['name'],
         'url': result['url'],
         'snippet': snippet} for result in results_with_content
        for snippet in split_content(result['content'], 300)
    ]

    documents = [gpt_index.Document(result['snippet'], extra_info={
                                    'url': result['url']}) for result in results_with_split_content]

    index = gpt_index.GPTSimpleVectorIndex(documents)

    response = index.query(question, mode="embedding")
    return response.response.strip('\n').strip()