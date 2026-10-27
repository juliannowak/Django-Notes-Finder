import os
import mido

def midi_to_text(midi_file_path, output_txt_path=None):
    """
    Converts a binary MIDI file into a human-readable raw text event list.
    """
    if not os.path.exists(midi_file_path):
        return f"Error: File '{midi_file_path}' not found."
    
    try:
        mid = mido.MidiFile(midi_file_path)
        output = []
        
        # File Metadata Header
        output.append(f"MIDI File: {os.path.basename(midi_file_path)}")
        output.append(f"Type: {mid.type} | Tracks: {len(mid.tracks)} | Ticks Per Beat: {mid.ticks_per_beat}\n")
        
        # Iterate over tracks and individual messages
        for i, track in enumerate(mid.tracks):
            output.append(f"--- Track {i}: {track.name if hasattr(track, 'name') else 'Unnamed'} ---")
            absolute_time = 0
            for msg in track:
                absolute_time += msg.time
                # Differentiate between system metadata and note instructions
                if msg.is_meta:
                    output.append(f"  [Time:{absolute_time:5d} / Delta:{msg.time:4d}] META: {msg}")
                else:
                    output.append(f"  [Time:{absolute_time:5d} / Delta:{msg.time:4d}] MIDI: {msg}")
            output.append("") # Blank line separator between tracks
            
        text_content = "\n".join(output)
        
        # Write to file if a path is provided
        if output_txt_path:
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"Success! Saved text breakdown to: {output_txt_path}")
        
        return text_content

    except Exception as e:
        return f"An error occurred while parsing the MIDI file: {str(e)}"


import os
path = os.path.join(os.getcwd(), "media", "MidiWorld")
midi_to_text(path, "midi_output.txt")