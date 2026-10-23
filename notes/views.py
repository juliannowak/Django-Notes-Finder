import site

from django.conf.locale import it
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
from urllib.parse import urlparse

SEARCH_SITES = [mw,] #bm, fm] #TODO add more sites, and create an enum

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
    results = models.Search.objects.filter(search_term=search_term).first()
    if results is None:
        for site in SEARCH_SITES:
            mod = site #TODO refactor site into module and site_name, getting rid of site variable entirely
            site_name = site.__name__[5:] #TODO add spaces between capitals
            search = getattr(site, "search", None)
    
            if search:
                print(f"{site.__name__} found:", search(search_term).keys())
                dictMidi = site.search(search_term)
                results = models.Search.objects.create(search_term=search_term, dictMidi=dictMidi) #add result to db
                
                #move this to run on server initialization.
                try:
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, site_name))
                    # os.makedirs(os.path.join(settings.MEDIA_ROOT, 'bm'))
                    # os.makedirs(os.path.join(settings.MEDIA_ROOT, 'fm'))
                except FileExistsError:
                    pass

                #use search results to download midi files
                scrape = getattr(site, "scrape", None)
                if scrape:
                    site.scrape(dictMidi, os.path.join(settings.MEDIA_ROOT, site_name))
                    print(f"Scraped {site_name} successfully")
                else:
                    print(f"{site_name} does not have a scrape function.")
                #bm.scrape(dictBitMidi, os.path.join(settings.MEDIA_ROOT, 'BitMidi'))
                #fm.scrape(dictFreeMidi, os.path.join(settings.MEDIA_ROOT, 'FreeMidi'))
                
                #use search results to add midi results and sheet music results to db
                # TODO thread and upload sheet music into folders by file name, track numbers, transposition
                for key, value in dictMidi.items():
                    fileName = key + '.mid'
                    print(fileName)
                    midi = os.path.join(settings.MEDIA_ROOT, site_name, fileName)
                    models.Midi.objects.create(name=fileName, file=midi, results=results, site=site_name)
                    print(f"Created new Midi object from {fileName}")
                    #TODO decide whether site field should be the name or module
                    
                    #count_tracks = make_notes(midi, 'C', '0') #TODO change to actual keys and tracks
                    #TODO thread: models.Sheet.objects.create()
                    
            else:
                print(f"{site.__name__} does not have a search function.")
        
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
    #TODO FIX
    search_result = models.Search.objects.filter(search_term=search_term).first()
    if search_result is None:
        return HttpResponse("Not Found")

    # results is a foreign key on Midi, so values() returns its integer ID
    midi_result = models.Midi.objects.filter(results=search_result).first()
    if midi_result is not None:
        site = midi_result.site
        results = search_result.dictMidi
        print(f"Results for {search_term} on {site}: {results}")
            
        midi_paths = [] #my urls
        site_urls = []
        for name, url in results.items():
            site_urls.append(url)
            path = os.path.join(settings.MEDIA_ROOT, site, name + '.mid')
            #print(path)
            midi_paths.append(path)
        results = list(zip(results.keys(), midi_paths, [site], site_urls))
        print(results[0])
    else:
        return HttpResponse("Not Found")

    return render(request, 'results.html', { 'midi_results': results})

    
    
    
    #create transpositsons
    # count_tracks = []
    # for result in results.keys():
    #     midi_path = os.path.join(settings.MEDIA_ROOT, 'Midi World', result + '.mid')
    #     print(midi_path)
    #     count_tracks.append(make_notes(midi_path, 'C', '0')) #TODO change to actual keys and tracks
    # results = zip(results.keys(), results.values(), count_tracks) #TODO change to dict with midi name, link, and number of tracks   
    
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