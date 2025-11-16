from django.db import models

# Create your models here.

class Search(models.Model):
    search_term = models.CharField(max_length=200)
    dictMidi = models.JSONField(default=dict) #rename to dictMidi -> (midi_name: midi_link)
    #count_usage = models.SmallIntegerField()
    #created_at = models.DateTimeField(auto_now_add=True)

class MidiResult(models.Model):
    midi_name = models.CharField(max_length=200)
    file_midi = models.FilePathField()
    file_notes_pdf = models.FilePathField()
    #file_png or jpg
    results = models.ForeignKey(Search, on_delete=models.CASCADE, related_name="results") #access by search.results.all()
    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'