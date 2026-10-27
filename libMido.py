"""
A class / library for MIDI file processing using Mido.

notes -> measures -> bars (lines) -> tracks (voice / instrument) -> composition (sheet / song)
requirements: lilypond installed and added to $PATH or to the environment variable Path
"""
import glob
from tkinter import NO
DEBUG = True
from matplotlib.pyplot import bar
import mingus
import mingus.midi.midi_file_in as MidiIn
import mingus.extra.lilypond as LilyPond
from mingus.containers import Bar, NoteContainer, Track, Composition
import mido
from music21 import stream, note, instrument, converter

def trackToComposition(track):
    out_comp = Composition()
    out_track = Track()
    [print(f"{bar.meter}") for bar in track.bars]
    [out_track.add_bar(bar) for bar in track.bars]
    out_comp.add_track(out_track)
    return out_comp

def break_on_double_bar(ly_string):
    # Replace all double bar lines with a double bar followed by a break
    # Use \\\\ for a literal backslash in a non-raw string
    return ly_string.replace('\\bar "||"', '\\section \\break')
    #return ly_string.replace('\\bar "||"', '\\bar "||" \\break')

def break_on_single_bar(ly_string, measures_per_line=4, has_pickup=False):
    new_music = ""
    bars = ly_string.split('|')
    # Start counter at -1 if the first bar is a pickup
    counter = -1 if has_pickup else 0
    # consider adding \partial to pickup notes

    for i, bar in enumerate(bars):
        # Add the music back plus the bar line
        new_music += bar + "|"
        # # Check if we are at the 4th bar (and not the very last bar)
        if (i + 1 + abs(counter)) % 4 == 0:
            new_music += " \\break "

    return new_music

def is_pickup_measure(bar, meter=(4, 4)):
    # Calculate the total duration of all notes/rests in the bar
    # mingus notes have a 'duration' attribute (e.g., 4 for quarter, 8 for eighth)
    # The 'weight' of a bar is the sum of (1 / duration)
    current_weight = sum([1.0 / n.duration for n in bar.notes])
    
    # Expected weight for the meter (e.g., 4/4 = 1.0, 3/4 = 0.75)
    expected_weight = meter[0] / meter[1]
    
    # If the bar is significantly shorter than the expected weight, it's a pickup
    return current_weight < expected_weight

    # Usage:
    # track = your_composition.tracks[0]
    # first_bar = track.bars[0]

    # if is_pickup_measure(first_bar, track.meter):
    #     print("This is a pick-up measure!")

def fix_overfull_bars(track):
    max_beats = track.meter[0]  # e.g., 4 for 4/4 time
    
    for bar in track.bars:
        if bar.current_beat > max_beats:
            # Calculate the overflow amount
            overflow = bar.current_beat - max_beats
            
            # Get the last note/event added to the bar
            if bar.notes:
                last_event = bar.notes[-1]
                # 'duration' in mingus is 1/n (e.g., 4 for quarter note)
                # We need to convert duration to beats to subtract the overflow
                current_note_beats = 1.0 / last_event[1] 
                new_beats = current_note_beats - overflow
                
                # Update the note's duration (ensure it's not zero or negative)
                if new_beats > 0:
                    last_event[1] = 1.0 / new_beats
                else:
                    bar.notes.pop() # Remove it if it's entirely overflow
            
            # Force the bar's internal counter to reset
            bar.current_beat = max_beats 

            # Apply to your tracks before converting to LilyPond
            # for track in your_composition.tracks:
            #     fix_overfull_bars(track)

def write_composition_old(comp, filename, tracks_to_skip=None):
    header = r"""
    \version "2.24.4"
    #(set-global-staff-size 14)
    #(ly:set-option 'crop #t)
    #(set-paper-size "a4")    % Set the physical page size
    \paper {
        top-margin = 10\mm        % Adjust margins to prevent clipping
        bottom-margin = 10\mm
        left-margin = 15\mm
        line-width = 180\mm       % Must match the layout's expectations
    }

    \layout {
        ragged-right = ##f
        \context {
            \Score
            % This forces LilyPond to allow breaks even if it thinks they look bad
            \override SpacingSpanner.strict-grace-spacing = ##t
            \override SpacingSpanner.strict-note-spacing = ##t
            forbidBreakBetweenBarLines = ##f
            override BarLine.transparent = ##f
            % This tells LilyPond "even if the math is wrong, draw the bar and allow a break"
            barCheckSynchronize = ##t 
        }
    }
"""
    stem = os.path.splitext(os.path.basename(filename))[0]
    output_dir = os.path.dirname(filename)
    if DEBUG:
        print("Track count:", len(comp.tracks))
    
    for i, track in enumerate(comp.tracks):
        if DEBUG:
            print(i, "bars:", len(track.bars))

        if len(track.bars) > 0:
            if DEBUG:
                current_meter = track.bars[0].meter
                print(f"The meter is: {current_meter}")
        else:
            print("track is empty or unknown meter")
            # Default to 4/4 if no meter is set
            # if track.meter is None:
            #     track.meter = (4, 4)
            # else:
            #     print(f"Track {i} has meter: {track.meter}")

        for bar in track.bars:
            if not bar.is_full():
                if DEBUG:
                    print(f"Bar {i} is underfull: {bar.current_beat}")
                bar.place_rest(bar.space_left())
            # Check if mingus allowed it to go over (rare but possible with some methods)
            if bar.current_beat > bar.meter[0]:
                if DEBUG: 
                    print(f"Bar {i} is OVERFULL! This is killing your breaks.")
    
        # if i in tracks_to_skip:
        #     continue
        
        ly_str = break_on_single_bar(
                break_on_double_bar(
                LilyPond.from_Composition(trackToComposition(track))))
        out_base = os.path.join(output_dir, f"{stem}_track{i}")
        LilyPond.to_png(header + ly_str, out_base)

def write_composition(comp, base_path):
    header = r"""
        \version "2.24.4"
        #(set-global-staff-size 14)
        #(ly:set-option 'crop #t)
        #(set-paper-size "a4")    % Set the physical page size
        \paper {
            top-margin = 10\mm        % Adjust margins to prevent clipping
            bottom-margin = 10\mm
            left-margin = 15\mm
            line-width = 180\mm       % Must match the layout's expectations
        }
    
        \layout {
            ragged-right = ##f
            \context {
                \Score
                % This forces LilyPond to allow breaks even if it thinks they look bad
                \override SpacingSpanner.strict-grace-spacing = ##t
                \override SpacingSpanner.strict-note-spacing = ##t
                forbidBreakBetweenBarLines = ##f
                override BarLine.transparent = ##f
                % This tells LilyPond "even if the math is wrong, draw the bar and allow a break"
                barCheckSynchronize = ##t 
            }
        }
    """

    filtered = mido.MidiFile(filtered_mid)
    print("filtered track count:", len(filtered.tracks))
    for i, track in enumerate(comp.tracks):
        print("track", i, "num messages:", len(track))
        if not track.bars:
            continue

        # Convert whole track, no dumb string splitting
        ly = LilyPond.from_Composition(trackToComposition(track))
        out_path = f"{base_path}_track{i}"

        # If you really need breaks, do it in the track structure
        # not by splitting the generated text
        LilyPond.to_png(header + ly, out_path)


def mido_parse(file):
    try:
        # Mido's parser is more lenient with SMF specifications
        #mid = mido.MidiFile(file)
        mid = mido.read_syx_file(file)

        # Saving it via mido reconstructs a standard header and message structure
        mid.save(file)
    except Exception as e:
        print(f"Failed to parse original file: {e}")

def nuclear_hex_cleaner(input_path, output_path):
    with open(input_path, 'r', errors='ignore') as f:
        content = f.read()

    # 1. Keep ONLY hexadecimal digits (0-9, A-F)
    # This ignores spaces, newlines, BOMs, and header text like "SYX"
    hex_only = "".join(c for c in content if c.upper() in "0123456789ABCDEF")
    
    # 2. Hex strings must have an even number of characters (2 chars per byte)
    if len(hex_only) % 2 != 0:
        hex_only = hex_only[:-1] 

    try:
        # 3. Manually convert hex string to binary bytes
        raw_bytes = bytes.fromhex(hex_only)
        
        # 4. Wrap the bytes in a Mido message and save as binary .syx
        # Syx files are just a stream of bytes starting with F0 and ending with F7
        with open(output_path, 'wb') as f:
            f.write(raw_bytes)
            
        print(f"Success! Created a binary file: {output_path}")
        print("You can now try opening this file in mingus.")
    except Exception as e:
        print(f"Failed at the binary step: {e}")

def force_clean_syx(input_path, output_path):
    with open(input_path, 'r', errors='ignore') as f:
        # Read as text and keep ONLY hexadecimal characters and spaces
        raw_text = f.read()
        clean_hex = "".join(c for c in raw_text if c.upper() in "0123456789ABCDEF ")
    
    # Write this back as a temporary clean text file
    temp_text_path = "temp_clean.txt"
    with open(temp_text_path, 'w') as f:
        f.write(clean_hex)
    
    try:
        # Now mido can read the sanitized text
        messages = mido.read_syx_file(temp_text_path)
        # Save it as a REAL binary MIDI/SYX file for mingus
        mido.write_syx_file(output_path, messages)
        print(f"Success! Saved binary file to: {output_path}")
    except Exception as e:
        print(f"Still failed: {e}")


def keep_part(part):
    inst = part.getInstrument()
    if inst is None:
        return True  # keep if unknown, or decide policy

    # percussion channel
    if hasattr(inst, "midiChannel") and inst.midiChannel == 9:
        return False

    # unpitched percussion class
    if isinstance(inst, instrument.UnpitchedPercussion):
        return False

    # actual unpitched notes in the part
    if len(part.recurse().getElementsByClass(note.Unpitched)) > 0:
        return False

    return True

def filter_percussion_tracks(input_mid, output_mid):
    try:
        score = converter.parse(input_mid)
    except Exception as e:
        raise RuntimeError(f"music21 could not parse {input_mid}: {e}")

    print("Parsed type:", type(score))
    print("Score repr:", score)
    #debug info
    print("score type:", type(score))
    print("has parts:", hasattr(score, "parts"))
    if hasattr(score, "parts"):
        print("parts count:", len(score.parts))

    # Some MIDI files parse as a single Part/Stream instead of a Score
    parts = []
    if hasattr(score, "parts"):
        parts = list(score.parts)
    if not parts:
        # find nested parts if this is a single stream
        parts = list(score.recurse().getElementsByClass(stream.Part))

    if not parts:
        raise ValueError(f"No musical parts found in {input_mid}. File may be empty or malformed.")

    kept_indexes = []

    for i, part in enumerate(parts):
        inst = part.getInstrument()
        print("part", i, "type:", type(part), "instrument:", inst)

        # If the instrument is percussion, drop it
        if inst is not None and (
            getattr(inst, "midiChannel", None) == 9 or
            isinstance(inst, instrument.UnpitchedPercussion)
        ):
            continue

        # Also drop obvious unpitched-percussion content
        if len(part.recurse().getElementsByClass(note.Unpitched)) > 0:
            continue

        kept_indexes.append(i)

    print("Keeping parts:", kept_indexes)

    filtered = stream.Score()
    if getattr(score, "metadata", None) is not None:
        filtered.insert(0, score.metadata)

    for idx in kept_indexes:
        filtered.insert(0, parts[idx])

    filtered.write('midi', fp=output_mid)

#remove next two
def music21_parse(input_file, output_file):
    try:
        # music21 parses MIDI into high-level musical 'Streams'
        score = converter.parse(input_file)
        score.write('midi', fp=output_file)
        print(f"Percussion Tracks: {percussion_track_numbers_filter(score)}")
    except:
        print(f"Error parsing {input_file} with music21")

def percussion_track_numbers_filter(score):
    # Create a new score to hold non-percussion parts
    #filtered_score = stream.Score()
    
    # Optional: Copy original metadata (title, composer, etc.)
    # if score.metadata:
    #     filtered_score.insert(0, score.metadata)
    
    filtered = []
    for i, part in enumerate(score.parts):
        inst = part.getInstrument()
        
        # 1. Check for MIDI Channel 9 (General MIDI Channel 10)
        is_perc_channel = (inst.midiChannel == 9)
        
        # 2. Check if the instrument is an unpitched percussion class
        is_perc_class = isinstance(inst, instrument.UnpitchedPercussion)
        
        # 3. Check for actual unpitched note objects in the stream
        has_unpitched = len(part.recurse().getElementsByClass(note.Unpitched)) > 0
        
        if is_perc_channel or is_perc_class or has_unpitched:
            filtered.append(i)

        # Add to the new score ONLY if none of the percussion flags are true
        # if not (is_perc_channel or is_perc_class or has_unpitched):
        #     filtered_score.insert(0, part)
            
    return filtered

#TODO rename process_midi()
def process(path=None):
    if path is not None:
        if not str(path).endswith("*.mid"): #check that it does with .mid AND is a file
            path += "/*.mid"
        print(path)
        count = 0
        for file in glob.glob(path):
            try:
                music21_parse(file, file)  # Parse and overwrite the same file
                #mido_parse(file)  # AVOID FOR NOW. Re-parse with mido to ensure it's well-formed
                #force_clean_syx(file, file)  # Clean and re-save as binary MIDI/SYX
                #nuclear_hex_cleaner(file, file)  # Aggressively clean hex and save as binary
                print(f"Parsed {file} successfully")
                count += 1
            
            except Exception as e:
                print(f"error parsing midi file: {e}")

            #convert midi to composition object compIn
            compIn, compInBPM = MidiIn.MIDI_to_Composition(file)
            
            #Roxanne: [0, 6]
            write_composition(compIn, file) 
    else:
        print("You need to pass in a path to the files you want to process for libMido to work.")

    print(f"Total files parsed: {count}")

import os
path = os.path.join(os.getcwd(), "media", "MidiWorld")
if not str(path).endswith("*.mid"): #check that it does with .mid AND is a file
    path += "/*.mid"
filtered_mid = "filtered.mid"
for file in glob.glob(path):
    stem = os.path.splitext(os.path.basename(file))[0]
    out_dir = os.path.join(os.getcwd(), "rendered", stem)
    os.makedirs(out_dir, exist_ok=True)

    filtered_mid = os.path.join(out_dir, f"{stem}_filtered.mid")

    filter_percussion_tracks(file, filtered_mid)

    mid_check = mido.MidiFile(filtered_mid)
    print("filtered track count:", len(mid_check.tracks))

    compIn, bpm = MidiIn.MIDI_to_Composition(filtered_mid)
    print("mingus track count:", len(compIn.tracks))

    write_composition(compIn, os.path.join(out_dir, stem))

#process(path)