from mingus.containers import Bar, NoteContainer, Track, Composition
import mingus.midi.midi_file_in as MidiIn
import mingus.extra.lilypond as LilyPond
import crawlMidiWorld as mw
import crawlBitMidi as bm
import crawlFreeMidi as fm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django import forms
from . import models
import mido
import os

SEARCH_SITES = ['MidiWorld']

def trackToComposition(track):
    out_comp = Composition()
    out_track = Track()
    [print(f"{bar.meter}") for bar in track.bars]
    [out_track.add_bar(bar) for bar in track.bars]
    out_comp.add_track(out_track)
    return out_comp

def make_notes(midi_path: str, keys: str, tracks: str):
    try:
        # Mido's parser is more lenient with SMF specifications
        mid = mido.MidiFile(midi_path)
        
        # Saving it via mido reconstructs a standard header and message structure
        mid.save(midi_path)
        compIn, compInBPM = MidiIn.MIDI_to_Composition(midi_path)


        # track = compIn.tracks[1]
        # print(len(track.bars))
        # numBars = len(track.bars)  # count

        #save entire composition for each key
        filename = os.path.splitext(os.path.basename(midi_path))[0]
        #filename = os.path.splitext(filename)[0]
        key='C' #temporary
        pdf_path = os.path.join(settings.MEDIA_ROOT,  filename, "pdf", key, f"FullScore.pdf" )
        png_path = os.path.join(settings.MEDIA_ROOT,  filename, "png", key, f"FullScore.png" )
        
        #save individual tracks
        notes = [] #paths to pdfs and pngs for each track
        for i, track in enumerate(compIn.tracks):
            if i == 2:
                break
            
            pdf_path = os.path.join(settings.MEDIA_ROOT,  filename, "pdf", key, f"Track {i}.pdf" )
            png_path = os.path.join(settings.MEDIA_ROOT,  filename, "png", key, f"Track {i}.png" )
            LilyPond.to_pdf(LilyPond.from_Composition(trackToComposition(track)),
                            pdf_path)
            LilyPond.to_png(LilyPond.from_Composition(trackToComposition(track)),
                            png_path)
            
            notes += pdf_path
            #notes += png_path

        print(f"Parsed {midi_path} successfully")
        #return notes
        return len(compIn.tracks)
    except Exception as e:
        print(f"Error parsing midi file {midi_path}: {e}")

def create_result(site_name):
    pass

#TODO rewrite as crawler object with list comps
def create_search(search_term: str):
    search = models.Search.objects.filter(search_term=search_term).first()
    if search is None:
        #note dictMidi = search results
        dictMidi = mw.search(search_term) #get search results from crawler, TODO thread and add to db as they are found instead of waiting for all results to be found before adding to db
        #dictBitMidi = bm.search(search_term)
        print(dictMidi.keys())
        search = models.Search.objects.create(search_term=search_term, dictMidi=dictMidi) #add results to db

        #move this to run on server initialization.
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'Midi World'))
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'Bit Midi'))
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'Free Midi'))
        except FileExistsError:
            pass

        #use search results download midi files, TODO thread and upload into folders by site name,
        mw.scrape(dictMidi, os.path.join(settings.MEDIA_ROOT, 'Midi World'))
        #bm.scrape(dictBitMidi, os.path.join(settings.MEDIA_ROOT, 'Bit Midi'))
        #fm.scrape(dictFreeMidi, os.path.join(settings.MEDIA_ROOT, 'Free Midi'))
        
        #use search results to add midi results and sheet music results to db
        # TODO thread and upload sheet music into folders by file name, track numbers, transposition
        for key, value in dictMidi.items():
            fileName = key + '.mid'
            print(fileName)
            midi = os.path.join(settings.MEDIA_ROOT, 'Midi World', fileName)
            models.Midi.objects.create(midi_name=fileName, file_midi=midi, results=search)

            #count_tracks = make_notes(midi, 'C', '0') #TODO change to actual keys and tracks
            #TODO thread: models.SheetMusic.objects.create()

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
    #get the results from a site
    results = models.Search.objects.filter(search_term=search_term).values('dictMidi').first()
    results = results['dictMidi']
    count_tracks = []
    for result in results.keys():
        midi_path = os.path.join(settings.MEDIA_ROOT, 'Midi World', result + '.mid')
        print(midi_path)
        count_tracks.append(make_notes(midi_path, 'C', '0')) #TODO change to actual keys and tracks
    results = zip(results.keys(), results.values(), count_tracks) #TODO change to dict with midi name, link, and number of tracks   

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
            # TODO add json results to form here
            create_search(instance.search_term)
            return redirect('results', search_term=instance.search_term)
        else:
            redirect('search')
    else:
        form = SearchForm()
    return render(request, 'search.html', {'form': form})

def midi(request, midi_name):
    #redirect()
    #models.MidiResult.objects.filter(midi_name)
    return render(request, 'midi.html', {'midi_name': midi_name})

def notes(request, midi_name):
    midi = models.MidiResult.objects.filter(midi_name)
    notes = models.Notes.objects.filter(midi)
    return render(request, 'notes.html', {'notes': notes})

def notes_by_tracks(request, midi_name, track):
    pass

def notes_by_transposition(request, midi_name, transposition):
    pass
    
def notes_by_both(request, midi_name, track, transposition):
    pass