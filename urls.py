from django.urls import path
from . import views
app_name="polls"
urlpatterns = [
    path('polls/', views.poll, name='poll'),
    path('polls/<int:id>/',views.all_poll, name='all_poll'),
    path('polls/<int:id>/update-vote/', views.update_vote, name='update_vote'),
    path('polls/tags/',views.tags,name='tags'),
    path('polls/<int:id>/details/', views.all_poll, name='details'),
    path('polls/<int:poll_id>/delete/', views.delete, name='delete'),
    path('polls/delete_tag/<str:tag_text>/', views.delete_tag, name='delete_tag'),
    path('polls/createpoll/',views.poll, name='poll'),
]
