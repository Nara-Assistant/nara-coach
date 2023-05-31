from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django import forms
from dotenv import load_dotenv

from .models import Question, avatars, diets, files as files_model, Users, Sessions, PresetQuestions, user_avatars, Prompts
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

load_dotenv('.env')

def train_files(files_to_train):
    for file_to_train in files_to_train:
        db_embeddings_utils.train_db(file_to_train[1], file_to_train[0])

@csrf_exempt
@require_http_methods(["POST"])
def train(request):
    """ Get pdf urls """
    try:
        avatar_path = request.headers.get('X-AVATAR-PATH') or ""

        # Find the avatar using the avatar_path
        try:
            avatar = avatars.objects.get(url_path=avatar_path)
        except avatars.DoesNotExist:
            return JsonResponse({"message": "AVATAR_NOT_FOUND"}, status=404)

        # Find the file IDs associated with the avatar
        files = files_model.objects.filter(avatar_id=avatar.id, file_type__in=["DIET_TRAINING", "TRAINING"])
        file_ids = [file.id for file in files]

        if not files:
            return JsonResponse({"message": "NOT_FOUND"}, status=404)

        files_to_train = [(file.id, file.file_url) for file in files]

        threading.Thread(target=train_files, args=[files_to_train]).start()

        return JsonResponse({"message": "SUCCESS"})
    except Exception as e:
        print(e)
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

