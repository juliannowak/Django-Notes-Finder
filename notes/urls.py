from django.urls import path
from . import views

urlpatterns = [
    #path('donate', views.donate, name='donate'),
    path('search', views.search, name='search'),
    path('search/<str:search_term>/', views.result, name='results'),
    #path('midi/<str:name>/', views.midi, name='midi'),
    #path('notes/<str:name>/', views.notes, name='notes'), #notes or composition or entire sheetmuisic
    #path('notes/<str:name>/track_pdf/<int:number>', views.track, name='track'),
    #path('notes/<str:name>/track_png/<int:number>', views.track, name='track'),
    #path('notes/<str:name>/track_png/<int:number>/transpositon', views.track, name='track'),
]
