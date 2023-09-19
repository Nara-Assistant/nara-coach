from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django import forms
from dotenv import load_dotenv

from .models import Question, avatars, diets, files as files_model, Users, Sessions, PresetQuestions, user_avatars, Prompts, TrainingQueue
from .decorators import supabase_auth_decorator
from .performance import perf_checker
from .notifications import send_notification

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
# import jwt
import hello.db_embeddings_utils as db_embeddings_utils
import threading
import requests
from .dbconnect import emb_conn

load_dotenv('.env')

# def update_welcome_message(avatar_id):
#     url = 'https://nara-agi-oq9f.zeet-nara.zeet.app/update_welcome_message'
#     headers = {'Content-Type': 'application/json'}
#     data = {"avatar_id": avatar_id}
#     response = requests.post(url, headers=headers, json=data)
#     if response.status_code == 200:
#         print("Welcome message updated successfully.")
#     else:
#         print("Failed to update welcome message.")

def train_files(files_to_train, avatar_id, queue_id):

    for file_to_train in files_to_train:
        db_embeddings_utils.train_db(file_to_train[1], file_to_train[0], file_to_train[2], avatar_id)

    current_queue = TrainingQueue.objects.filter(avatar_id= avatar_id, status = "IN_PROGRESS", id=queue_id).first()
    
    if current_queue is not None:
        current_queue.status = "DONE"
        # update_welcome_message(avatar_id)
        current_queue.save()
    

@csrf_exempt
@require_http_methods(["POST"])
def execute_from_queue(request):
    """ Get pdf urls """
    try:

        in_progress_queue_count = TrainingQueue.objects.filter(status = "IN_PROGRESS").count()

        if in_progress_queue_count >= 5:
            return JsonResponse({"message": "SUCCESS"})

        avatar_id = request.headers.get('X-AVATAR-ID') or ""
        queue_id = request.headers.get('X-QUEUE-ID') or ""
        
        current_queue = TrainingQueue.objects.filter(avatar_id= avatar_id, status = "PENDING", id=queue_id).first()

        if current_queue is None:
            return JsonResponse({"message": "ERROR"}, status=404)

        current_queue.status = "IN_PROGRESS"
        current_queue.save()
        files = None
        if current_queue.files_ids is not None:
            file_ids = json.loads(current_queue.files_ids)
            files = files_model.objects.filter(avatar_id=avatar_id, file_type__in=["DIET_TRAINING", "TRAINING"], id__in=file_ids)
        else:
            # Find the file IDs associated with the avatar
            files = files_model.objects.filter(avatar_id=avatar_id, file_type__in=["DIET_TRAINING", "TRAINING"])

        if not files:
            return JsonResponse({"message": "NOT_FOUND"}, status=404)

        files_to_train = [(file.id, file.file_url, file.raw_data) for file in files]


        threading.Thread(target=train_files, args=[files_to_train, avatar_id, queue_id]).start()

        return JsonResponse({"message": "SUCCESS"})
    except Exception as e:
        print(e)
        return JsonResponse({"message": "ERROR"}, status=500)



@csrf_exempt
@require_http_methods(["POST"])
def train(request):
    """ Get pdf urls """
    try:
        avatar_path = request.headers.get('X-AVATAR-PATH') or ""
        files_ids = request.headers.get('X-FILES-IDS') or None
        chunk_id = request.headers.get('X-CHUNK-ID') or None
        files_ids = json.loads(files_ids) if files_ids is not None else None

        # Find the avatar using the avatar_path
        try:
            avatar = avatars.objects.get(url_path=avatar_path)
        except avatars.DoesNotExist:
            return JsonResponse({"message": "AVATAR_NOT_FOUND"}, status=404)
        
        current_queue = TrainingQueue.objects.filter(avatar_id= avatar.id, status = "PENDING").first()

                
        if current_queue is None or files_ids is not None:
            (TrainingQueue(chunk_id = chunk_id, avatar_id= avatar.id, status = "PENDING", files_ids=None if files_ids is None else json.dumps(files_ids))).save()
        return JsonResponse({"message": "SUCCESS"})

    except Exception as e:
        print(e)
        send_notification("train_request", "nara-heroku", [("e", str(e))])
        return JsonResponse({"message": "ERROR"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_prompt(request):
    """ Get pdf urls """
    print("mmmm")
    avatar_path = request.headers.get('X-AVATAR-PATH') or ""

    # Find the avatar using the avatar_path
    try:
        avatar = avatars.objects.get(url_path=avatar_path)
    except avatars.DoesNotExist:
        return JsonResponse({"message": "AVATAR_NOT_FOUND"}, status=404)

    # Find the file IDs associated with the avatar
    files = files_model.objects.filter(avatar_id=avatar.id)
    file_ids = [file.id for file in files]

    question_asked = json.loads(request.body)["question"]
    try:
        print(file_ids)
        response = db_embeddings_utils.build_prompt(question_asked, file_ids)
        print(response)
        return JsonResponse({"message": "SUCCESS", "data": {"prompt": response}}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"message": "ERROR"}, status=500)

