from django.http import JsonResponse
from dotenv import load_dotenv

from .models import Users, Sessions

import jwt
import os

load_dotenv('.env')
JWT_SECRET = os.environ["JWT_SECRET"]

def supabase_auth_decorator(function):
    print("DECOR")
    def wrapper(request):
        print("DECORWRaPPER")
        try:
            authorization = request.headers.get('authorization')

            if authorization is None:
                return JsonResponse({
                    'message': 'ERROR'
                }, status=401)


            access_token = authorization.replace("Bearer ", "")
            decoded_token = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"], audience=["authenticated"])
            user_id, session_id= decoded_token["sub"], decoded_token["session_id"]
            user = Users.objects.filter(id=user_id).values().first()

            if user is None:
                return JsonResponse({
                    'message': 'ERROR'
                }, status=401)

            session = Sessions.objects.filter(user_id = user_id, id = session_id).values().first()

            if session is None:
                return JsonResponse({
                    'message': 'ERROR'
                }, status=401)
            supabase_data = {
                    "user_id": user_id,
                    "session_id": session_id
            }
            setattr(request, "supabase_data", supabase_data)
            func = function(request)

            return func
        except jwt.InvalidSignatureError:
            return JsonResponse({ "message": "ERROR", "data": "Invalid signature error"}, status = 401)
        except jwt.ExpiredSignatureError:
            return JsonResponse({ "message": "ERROR", "data": "Expired signature error"}, status = 401)
        except Exception as e:
            print(e)
            return JsonResponse({ "message": "ERROR"}, status = 500)

    return wrapper