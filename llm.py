import requests

from config import *


def get_free_models(openrouter_api_key=OPENROUTER_API_KEY):
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": openrouter_api_key
    }

    response = requests.get(url, headers=headers)
    models = response.json()
    free_models = []

    for item in models['data']:
        if 'free' in item['id']:
            free_models.append(item['id'])

    free_models.sort()
    return free_models
