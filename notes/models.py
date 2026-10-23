import os

from django.db import models
from urllib.parse import urlparse

# Search (results) contains multiple midi files, 
# so we have a one to many relationship between search and midi. 
# Midi can also have multiple sheet music results (transpositions and various tracks),
# so we have a one to many relationship between midi and sheet music.
# Upload is for midi files that users upload, and is separate from the search results. 
# We can use the uploaded midi files for our search algorithm to add to our database of midi files, 
# and also to test our search algorithm.

def get_midi_upload_path(instance, filename):
    site_name = instance.site if instance.site else "unknown"
    return os.path.join(site_name, filename)

def get_sheet_music_upload_path(instance, filename):
    site_name = instance.midi.site if instance.midi.site else "unknown"
    return os.path.join('sheet_music', site_name, filename)

class Upload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Search(models.Model):
    search_term = models.CharField(max_length=200)
    dictResults = models.JSONField(default=dict) # (site: midi_name)
    #TODO ensure midi_name is unique for each site
    dictMidi = models.JSONField(default=dict) #(midi_name: midi_link)
    #count_usage = models.SmallIntegerField()
    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Search:{self.search_term}'

class Midi(models.Model):
    name = models.CharField(max_length=200) #remove
    file = models.FileField(upload_to=get_midi_upload_path)
    url = models.URLField(max_length=255)
    
    # Add the field here and index it for lightning-fast lookups
    site = models.CharField(max_length=100, db_index=True, blank=True)

    #transpositon = models.SmallIntegerField() #with a whole tone = 2, so / 2 to change back
    # access by search.results
    results = models.ForeignKey(Search, 
                                on_delete=models.CASCADE, 
                                related_name="results") 
    #created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.url:
            domain = urlparse(self.url).netloc
            parts = [part for part in domain.split('.') if part != 'www']
            if parts:
                self.site = parts[0]
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Name:{self.name}'
    
class Sheet(models.Model):
    transposition = models.SmallIntegerField() #with a whole tone = 2, so / 2 to change back
    midi_track = models.SmallIntegerField()
    file_pdf = models.FilePathField()
    file_png = models.FilePathField()
    midi = models.ForeignKey(Midi,
                                on_delete=models.CASCADE,
                                related_name="midi") #access by search.results.all()

    def __str__(self):
        return f'Transposition:{str(self.transposition/2 or 0)}\nTrack:{self.midi_track}'
        #defaults to 0,0 for entire track, no transposition