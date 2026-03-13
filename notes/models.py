from django.db import models

# Search (results) contains multiple midi files, 
# so we have a one to many relationship between search and midi. 
# Midi can also have multiple sheet music results (transpositions and various tracks),
# so we have a one to many relationship between midi and sheet music.

class Search(models.Model):
    search_term = models.CharField(max_length=200)
    dictMidi = models.JSONField(default=dict) #rename to dictMidi -> (midi_name: midi_link)
    #count_usage = models.SmallIntegerField()
    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Search:{self.search_term}'

class Midi(models.Model):
    midi_name = models.CharField(max_length=200)
    file_midi = models.FilePathField()
    # TODO rename to search or term. access by search.results.all()
    results = models.ForeignKey(Search, 
                                on_delete=models.CASCADE, 
                                related_name="results") 
    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Name:{self.midi_name}'
    
class SheetMusic(models.Model):
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