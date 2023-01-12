from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv

from .models import Question, avatars, files as files_model

import pandas as pd
import openai
import numpy as np

from resemble import Resemble
import json
import os
import hello.utils as utils
import hello.files as file_module
import hello.bucket as bucket
import time
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlparse
from django.core import serializers

load_dotenv('.env')

@csrf_exempt
@require_http_methods(["POST"])
def train(request):
    """ Get pdf urls """
    avatar_path = request.headers['X-AVATAR-PATH']
    _avatar = avatars.objects.filter(url_path=avatar_path).values().first()

    if _avatar is None:
        print("404")
        # return 404

    # Get urls from database
    avatar_id = _avatar["id"]
    print(avatar_id)
    files_values = files_model.objects.filter(avatar_id=avatar_id, file_type='TRAINING').values()
    print(files_values)
    urls = [ x["file_url"] for x in files_values]
    print("llega2")
    ts = time.time()
    filename = f"{avatar_id}-{ts}"
    files = []

    #download files
    for url in urls:
        a = urlparse(url)
        files.append(f"{filename}-{os.path.basename(a.path)}")
        file_module.download_file(url, f"{filename}-{os.path.basename(a.path)}")
   
    
    dfs = utils.files_to_datasets(files)
    utils.create_files_by_dataframe(dfs, filename)
    bucket.upload_file(f"{filename}.embeddings.csv")
    bucket.upload_file(f"{filename}.pages.csv")

    files_model.objects.create(avatar_id=avatar_id, file_url=f"https://nara-files.s3.amazonaws.com/{filename}.embeddings.csv", file_type="EMBEDDINGS" )
    files_model.objects.create(avatar_id=avatar_id, file_url=f"https://nara-files.s3.amazonaws.com/{filename}.pages.csv", file_type="DATASET" )

    return JsonResponse({ "message": "SUCCESS" })


def get_file_from_url(url):
    a = urlparse(url)
    return f"{os.path.basename(a.path)}"

def download_csv(url, filename):
    file_module.download_file(url, filename)
 
@csrf_exempt
@require_http_methods(["POST"])
def ask(request):
    """ Get pdf urls """

    avatar_path = request.headers['X-AVATAR-PATH']
    _avatar = avatars.objects.filter(url_path=avatar_path).values().first()

    if _avatar is None:
        print("404")
        # return 404

    avatar_id = _avatar["id"]

    # Get urls from database
    dataset_url = files_model.objects.filter(avatar_id=avatar_id, file_type='DATASET').values().first()["file_url"]
    embeddings_url = files_model.objects.filter(avatar_id=avatar_id, file_type='EMBEDDINGS').values().first()["file_url"]
    print((dataset_url, embeddings_url))
    dataset_filename = get_file_from_url(dataset_url)
    embeddings_filename = get_file_from_url(embeddings_url)
    #download files
    
    download_csv(dataset_url, dataset_filename)
    download_csv(embeddings_url, embeddings_filename)
    question_asked = json.loads(request.body)["question"]
   
    if not question_asked.endswith('?'):
        question_asked += '?'

  
    previous_question = Question.objects.filter(question=question_asked).first()

    df = pd.read_csv(dataset_filename)
    document_embeddings = utils.load_embeddings(embeddings_filename)
    
    answer, context = utils.answer_query_with_context(question_asked, df, document_embeddings)

    project_uuid = '925953bd'
    voice_uuid = '9d89e4b3-george'
    try:
        print(( answer, context))
        # question = Question(question=question_asked, answer=answer, context=context)
        # question.save()
    except Exception as e:
        print(e)
        raise
        
    print("men")
    return JsonResponse({ "message": "SUCCESS", "data": { "question": question_asked, "answer": answer, "audio_src_url": "" }})
        
