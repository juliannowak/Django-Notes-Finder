"""
A class / library for MIDI file processing using Mingus.

notes -> measures -> bars (lines) -> tracks (voice / instrument) -> composition (sheet / song)

"""
import mingus
from mingus.containers import Bar, NoteContainer, Track, Composition
import mingus.extra.lilypond as LilyPond
import mingus.midi.midi_file_in as MidiIn
import mingus.extra.tablature as Tablature
import os
BARS_PER_TRACK = 2


def midiToComposition(file):
    return MidiIn.MIDI_to_Composition(file)[0]
    # MidiIn.MIDI_to_Composition(file)[1] is last BPM


def containerToMidi(outFile: str, container) -> None:
    from mingus.midi import MidiFileOut
    # write_Note, write_NoteContainer, write_Bar, write_Track and write_Composition
    container = NoteContainer(["A", "C", "E"])
    MidiFileOut.write_NoteContainer(outFile, nc)


def containerToPNG():
    b = Bar()
    b + "C"
    b + "E"
    b + "G"
    b + "B"
    bar = LilyPond.from_Bar(b)
    LilyPond.to_png(bar, "my_first_bar")

import os
from mingus.midi import midi_file_in as MidiIn

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "media", "MidiWorld", "Roxanne (The Police).mid")

# Run this directly without try/except to see the real error:
compIn, compInBPM = MidiIn.MIDI_to_Composition(file_path)
print("If you see this, it worked!")

# script_dir = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(script_dir, "media", "MidiWorld", "Roxanne (The Police).mid")

# with open(file_path, "rb") as file:
#     midi_data = file.read()
#     try:
#         compIn, compInBPM = MidiIn.MIDI_to_Composition(file)
#     except:
#         print("error")
    # parser = MidiIn.MidiFile()
    # with open(file, "rb+") as ptrFile:
    #     print(f"${parser.parse_midi_file_header(ptrFile)}")
    # print(MidiIn.MIDI_to_Composition(file)[1])


    #track = compIn.tracks[1]
    # print(len(track.bars))
    # numBars = len(track.bars)  # count


    # def trackToComposition(track):
    #     out_comp = Composition()
    #     out_track = Track()
    #     [print(f"{bar.meter}") for bar in track.bars]
    #     [out_track.add_bar(bar) for bar in track.bars]
    #     out_comp.add_track(out_track)
    #     return out_comp


    # for i, track in enumerate(compIn.tracks):
    #     if i == 2:
    #         break
    #     LilyPond.to_png(LilyPond.from_Composition(trackToComposition(track)),
    #                     f"test{i}")
    # LilyPond.to_png(LilyPond.from_Composition(out_comp), f"test")
    # LilyPond.to_png(LilyPond.from_Track(out_track), f"test")
    # for i, bar in enumerate(track.bars):
    #     out_track.add_bar(bar)

    #     if (i % BARS_PER_TRACK == 0):
    #         out_track = Track()

    # [out_track.add_bar(track.bars[x]) for x in range(4)]
    # LilyPond.to_png(LilyPond.from_Bar(out_bar), "test")
