from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url(r'^crawl/', views.crawl, name='crawl'),
    url(r'^getterms/', views.get_terms  , name='get_terms'),
    url(r'^index/', views.index, name='index'),

]