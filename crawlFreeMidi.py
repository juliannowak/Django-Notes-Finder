import os
from datetime import datetime
import argparse
from requests_html import HTMLSession, AsyncHTMLSession
session = HTMLSession()

def search(search: str = '') -> dict[str, str]:
    search = search.replace(' ', '+')
    res = session.get('https://www.freemidi.org/search?q=' + search)
    # if res:
    #     print("Request successful")
    # else:
    #     print("Request failed with status code:", res.status_code)
    # Use 'contains' for both text and class to be safe
    # 1. Grab every single element that could be relevant
    all_els = res.html.find('h2, div.container')

    # 2. Use a flag to "trigger" the search once we hit 'Songs'
    found_h2 = False

    for el in all_els:
        # Look for the header first
        if not found_h2 and 'Songs' in el.text:
            found_h2 = True
            continue
        
        # Once the header is found, the very next div.container we hit is our target
        results = {}
        if found_h2 and 'container' in el.attrs.get('class', []):
            cards = el.find('div.card-body')
            for card in cards:
                link = card.find('a', first=True)  # This is the link to the song
                if link and link.attrs['href'].startswith("down"): # Only add it if it's a download link
                    results[link.text] = link.attrs.get('href', '')
            break # We found it, so we can stop the loop

    #print(list(results.values()))
    #exit()
    return results


#TODO problem; it is getting links from categories, not just songs
def scrape(data, path=''):
    for key, value in data.items():
        print(f"Processing {key} with link {value}...")
        midi_page = session.get('https://www.freemidi.org/' + value)
        #midi_page.html.render()
        midi_link = midi_page.html.find('a#downloadmidi', first=True)
        midi_link = 'https://www.freemidi.org/' + midi_link.attrs.get('href', '')
        print(f"Downloading {key} from {midi_link}...")
        if midi_link is None:
            print(f"Could not find MIDI link for {key}, skipping.")
            continue
        midi = session.get(midi_link, stream = True) 
    
        if path != '':
            fileName = os.path.join(path, key)
        else:
            fileName = key
        print("Saving %s" % fileName)
        
        with open(fileName + '.mid', 'wb') as file:
            for chunk in midi.iter_content(chunk_size=1024):
                # writing one chunk at a time
                if chunk: 
                    file.write(chunk)

#TODO fix path variable, it is not working as intended, it is saving to the current directory instead of the provided path
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrapes Free Midi',
                                    prog='crawlFreeMidi',
                                    epilog='\nthank you')
    parser.add_argument('searchTerm',
                        help="a string to search for results with\nif it has spaces, enclose it with double quotes",)       #required
    parser.add_argument('-q', '--query',    #optionals
                        help="outputs the resulting titles and links to the console, in JSON form",
                        action='store_true')
    parser.add_argument('-d', '--download',
                        help="downloads the results, .mid",
                        action='store_true')
    parser.add_argument('-j', '--json',
                        help="downloads the resulting titles and links, .json",        
                        action='store_true')
    parser.add_argument('-c', '--csv',
                        help="downloads the results, .csv",         
                    action='store_true')
    parser.add_argument('-v', '--verbose',
                        help="outputs additional info, only useful in debugging",
                        action='store_true')
    parser.add_argument('-p', '--path',
                        help="a path to save downloads to",)
    
    args = parser.parse_args()

    if args.searchTerm != None:
        if args.verbose:
            print(args.searchTerm)
        
        if args.path == None:
            print("No path provided, saving to FreeMidi folder in current directory")
            args.path = os.path.join(os.getcwd(), "FreeMidi")
            if not os.path.exists(args.path):
                os.makedirs(args.path)
        else:
            if not os.path.isabs(args.path):
                print("Provided path is not absolute, converting to absolute path")
                args.path = os.path.join(os.getcwd(), args.path)
            else:
                print("Provided path is absolute, using as is.")
            
        print("Using %s" % args.path)
            
        results = search(args.searchTerm)
        
        if args.query is True:
            print(results) # intentional print of the dict, not json, for better readability in the console -AI
            
            if args.download is True:
                import json
                
                jsonQuery = json.dumps(results)
                currentTime = datetime.now()
                
                name = os.path.join(args.path, args.searchTerm + currentTime)
                with open(name, 'wb') as f:
                    f.write(jsonQuery)
            
        if args.download is True:
            scrape(results, args.path)            
else:
    print("running from import")
    
#scrape(search("american"))