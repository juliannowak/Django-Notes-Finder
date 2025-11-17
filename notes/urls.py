from django.urls import path
from . import views

urlpatterns = [
    #path('donate', views.donate, name='donate'),
    path('search', views.search, name='search'),
    path('search/<str:search_term>/', views.result, name='results'),
    path('midi/<str:midi_name>/', views.midi, name='midi'), #midi don't need transposition
    #path('notes/<str:midi_name>/', views.notes, name='notes'), #notes or composition or entire sheet music
    #path('notes/<str:midi_name>/<int:track>/', views.notes, name='notes'),
    #path('notes/<str:midi_name>/track_pdf/<int:number>', views.track, name='track'),
    #path('notes/<str:midi_name>/track_png/<int:number>', views.track, name='track'),
    #path('notes/<str:midi_name>/track_png/<int:number>/transpositon', views.track, name='track'),
]
