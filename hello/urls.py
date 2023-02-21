from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import hello.views
import hello.api

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
    
    # path("api/test", hello.api.test, name="test")
]
