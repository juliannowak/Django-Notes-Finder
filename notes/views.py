from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import forms
from django.conf import settings
from mingus.containers import Bar, NoteContainer, Track, Composition
import mingus.midi.midi_file_in as MidiIn
import mingus.extra.lilypond as LilyPond
from . import models
import crawlMidiWorld as mw
import crawlBitMidi as bm
import os

SEARCH_SITES = ['MidiWorld']

def trackToComposition(track):
    out_comp = Composition()
    out_track = Track()
    [print(f"{bar.meter}") for bar in track.bars]
    [out_track.add_bar(bar) for bar in track.bars]
    out_comp.add_track(out_track)
    return out_comp

def make_notes(midi_path: str, site: str):
    try:
        compIn, compInBPM = MidiIn.MIDI_to_Composition(midi_path)
    except:
        print("error")
    
    # track = compIn.tracks[1]
    # print(len(track.bars))
    # numBars = len(track.bars)  # count

    notes = []
    for i, track in enumerate(compIn.tracks):
        if i == 2:
            break
        filename = os.path.basename(midi_path)
        filename = os.path.splitext(filename)[0]
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'Midi World', f"{filename}{i}")
        LilyPond.to_pdf(LilyPond.from_Composition(trackToComposition(track)),
                        pdf_path)
        notes += pdf_path
        return notes
        # LilyPond.to_pdf(LilyPond.from_Composition(out_comp),os.path.join(settings.MEDIA_ROOT, 'Midi World', f"{filename} all tracks")

#TODO rewrite as crawler object with list comps
def create_search(search_term: str):
    search = models.Search.objects.filter(search_term=search_term).first()
    if search is None:
        dictMidi = mw.search(search_term)
        #dictBitMidi = bm.search(search_term)
        #print(dictMidi.keys())
        search = models.Search.objects.create(search_term=search_term, dictMidi=dictMidi)
        #TODO create_result(site_name)
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'Midi World'))
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'Bit Midi'))
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'Free Midi'))
        except FileExistsError:
            pass
        #download midis, TODO thread and upload into folders further by file name, track number, transposition ?
        mw.scrape(dictMidi, os.path.join(settings.MEDIA_ROOT, 'Midi World'))
        #bm.scrape(dictBitMidi, os.path.join(settings.MEDIA_ROOT, 'Bit Midi'))
        #fm.scrape(dictFreeMidi, os.path.join(settings.MEDIA_ROOT, 'Free Midi'))
        
        for name in dictMidi.keys():
            midi = os.path.join(settings.MEDIA_ROOT, 'Midi World', name)
            #notes = make_notes(midi)
            # if notes:
            #     pass
            #print(notes)
            models.MidiResult.objects.create(midi_name=name, file_midi=midi, results=search)
            #TODO thread: models.Notes.objects.create()

#FORMS
class SearchForm(forms.ModelForm):
    class Meta:
        model = models.Search
        fields = ('search_term',)
        labels = {
            'search_term': '',
        }

#VIEWS
def result(request, search_term):
    results = models.Search.objects.filter(search_term=search_term).values('dictMidi').first()
    results = results['dictMidi']
    results = zip(results.keys(), results.values())
    if results == None:
        return HttpResponse("not found")
    else:
        return render(request, "results.html", {'results': results})
    
def search(request):
    #handle form action (search)
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False) # Don't save yet
            #print(instance.search_term)
            # TODO add json to form here
            create_search(instance.search_term)
            return redirect('search/%s' % instance.search_term)
        else:
            redirect('search')
    else:
        form = SearchForm()
    return render(request, 'search.html', {'form': form})

def midi(request, midi_name):
    #redirect()
    #models.MidiResult.objects.filter(midi_name)
    return render(request, 'midi.html', {'midi_name': midi_name})

def notes(request):
    pass