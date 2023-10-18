from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import hello.views
import hello.api
import hello.db_embeddings_api

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", hello.views.index, name="index"),
    path("ask", hello.views.ask, name="ask"),
    path("question/<int:id>", hello.views.question, name="question"),
    path("db", hello.views.db, name="db"),
    path("admin/", admin.site.urls),
    path("api/train", hello.api.train, name="train"),
    path("api/ask", hello.api.ask, name="ask"),
    path("api/image/upload", hello.api.image_upload, name="image_upload"),
    path("api/prompt/build", hello.api.get_prompt, name="build-prompt"),
    path("api/v2/prompt/build", hello.api.get_prompt_v2, name="build_prompt_v2"),
    path("api/v2/train", hello.api.train_diet, name="train_v2"),
    path("api/health-check", hello.api.health_check, name="health_check"),
    path("api/v3/prompt/build", hello.db_embeddings_api.get_prompt, name="build_prompt_v3"),
    path("api/v3/train", hello.db_embeddings_api.train, name="train_v3"),
    path("api/v3/queue/execute", hello.db_embeddings_api.execute_from_queue, name="execute_from_queue"),
    path("api/v3/get-valid-files", hello.db_embeddings_api.get_valid_files, name="get_valid_files"),

    
    
    # path("api/test", hello.api.test, name="test")
]
