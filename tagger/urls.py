from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^corpus$', views.corpus, name='corpus'),
    url(r'^test$', views.test, name='test'),
]