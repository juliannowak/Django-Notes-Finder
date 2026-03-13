from django.urls import path
from . import views

urlpatterns = [
    #path('donate', views.donate, name='donate'),
    path('search/', views.search, name='search'),
    path('search/<str:search_term>/', views.result, name='results'),
    path('midi/<str:midi_name>/', views.midi, name='midi'), #midi, all tracks, no transpositions (can easily be done in preffered DAW)
    path('notes/<str:midi_name>/', views.notes, name='notes'), # all tracks, or the entire sheet music composistion
    #path('notes/<str:midi_name>/<int:track>/', views.notes, name='notes'), #notes by track
    #path('notes/<str:midi_name>/track_pdf/<int:number>', views.track, name='track'),
    #path('notes/<str:midi_name>/track_png/<int:number>', views.track, name='track'),
    #path('notes/<str:midi_name>/track_png/<int:number>/transpositon', views.track, name='track'),
]
