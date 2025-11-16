import os
from datetime import datetime
from requests_html import HTMLSession, AsyncHTMLSession
session = HTMLSession()

def download_file(url, local_filename):
    # NOTE the stream=True parameter below
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=None): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                if chunk: 
                    f.write(chunk)

def lists2dict(keyList, valueList):
    #print("# of keys: {}\n# of values: {}\nkeys: {}\nvalues: {}".format(len(keyList), len(valueList), keyList, valueList))
    # using the fromkeys() method to create a dictionary
    result_dict = dict.fromkeys(keyList)
    # iterating through the dictionary and updating values
    for key, value in zip(result_dict.keys(), valueList):
        result_dict[key] = value
    
    return result_dict

def search(search: str = '') -> dict[str, str]:
    search = search.replace(' ', '+')
    res = session.get('https://www.midiworld.com/search/?q=' + search)
    
    res = res.html.find(selector='#page', first=True, clean=True)
    resLists = res.find(selector='li')
    
    links = []
    songs = []
    for result in resLists:
        if ("Please" in result.text.split()):
            end = result.text.index(" - download")
            songs.append(result.text[:end])
            link = result.find('a', first=True)
            links.append(link.attrs['href'])
            
    #links = [result.attrs['href'] for result in resLinks]
    #links = links[:len(songs)]
    
    return lists2dict(songs,links)

def scrape(data: dict, path=''):
    for song in data.keys():
        midi = session.get(data[song], stream = True) 
        
        fileName = song
        if path != '':
            fileName = os.path.join(path, song)
        
        with open(fileName + '.mid', 'wb') as file:
            for chunk in midi.iter_content(chunk_size=1024):
                # writing one chunk at a time
                if chunk: 
                    file.write(chunk) 

if __name__ == "__main__":
    print("running directly")
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrapes Midi World',
                                    prog='crawlMidiWorld',
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
    
    
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator') #list of integer args
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                     const=sum, default=max,
    #                     help='sum the integers (default: find the max)') #boolean flag like function holder
    
    args = parser.parse_args()
    #print(args.accumulate(args.integers))
    
    if args.searchTerm != None:
        if args.verbose:
            print(args.searchTerm)
        
        #handle absolute paths
        if args.path == None:
            print("yo")
            args.path = os.path.join(os.getcwd(), "MidiWorld")
        else:
            args.path = os.path.join(os.getcwd())
            
        results = search(args.searchTerm)
        
        if args.query is True:
            print(results)
            
            if args.download is True:
                import json
                
                jsonQuery = json.dumps(results)
                currentTime = datetime.now()
                
                name = os.path.join(args.path, args.searchTerm + currentTime)
                with open(name, 'wb') as f:
                    f.write(jsonQuery)
            
        if args.download is True:
            scrape(results)            
else:
    print("running from import")
#scrape(search('blink 182'))
