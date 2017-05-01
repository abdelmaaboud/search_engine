from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.search, name='search'),
    url(r'^search/$', views.search,name="search"),

    #url(r'^crawl/', views.crawl, name='crawl'),
    #url(r'^getterms/', views.get_terms  , name='get_terms'),
    #url(r'^index/', views.get_index, name='get_index'),

]