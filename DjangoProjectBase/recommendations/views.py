import os

import numpy as np
from django.conf import settings
from django.shortcuts import render
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from movie.models import Movie

# ✅ Load the OpenAI API key from the openAI.env file at the root of the repository
load_dotenv(settings.BASE_DIR.parent / 'openAI.env')


def get_embedding(text):
    client = OpenAI(api_key=os.environ.get('openai_apikey'))
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def recommendations(request):
    prompt = request.GET.get('prompt', '').strip()
    best_movie = None
    max_similarity = -1
    error = None

    if prompt:
        try:
            prompt_emb = get_embedding(prompt)
        except OpenAIError as e:
            error = f"Could not get the embedding of the prompt from OpenAI: {e}"
        else:
            # ✅ Compare the prompt against every movie and keep the most similar one
            for movie in Movie.objects.all():
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                # Movies without a generated embedding keep the random default, which has a different size
                if movie_emb.shape != prompt_emb.shape:
                    continue
                similarity = cosine_similarity(prompt_emb, movie_emb)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_movie = movie

    return render(request, 'recommendations.html', {
        'prompt': prompt,
        'movie': best_movie,
        'similarity': max_similarity,
        'error': error,
    })
