from requests_html import HTMLSession, AsyncHTMLSession
import datetime
import os
import argparse

session = HTMLSession()

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
    res = session.get('https://bitmidi.com/search?q=' + search)
    articles = res.html.find(selector='article', clean=False)
    
    songs, links = [], []
    for article in articles:
        link = article.find(selector='a',first=True)
        song = link.find(selector='h2', first=True)
        links.append(link.attrs['href'])
        songs.append(song.text)
        
    return lists2dict(songs,links)
    
def scrape(data: dict, path: str = ''):
    for key, value in data.items():
        midi = session.get('https://bitmidi.com/' + value, stream = True) 

        if path != '':
            fileName = os.path.join(path, key)
        else:
            fileName = key

                # Check if the file already exists
        fileName = os.path.join(path, key) if path else key
        if os.path.exists(fileName + '.mid'):
            print(f"File {fileName + '.mid'} already exists, skipping download.")
            continue

        with open(fileName + '.mid', 'wb') as file:
            print("Saving %s" % fileName)
            for chunk in midi.iter_content(chunk_size=1024):
                # writing one chunk at a time
                if chunk: 
                    file.write(chunk) 

if __name__ == "__main__":
    print("running directly")
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrapes Bit Midi',
                                    prog='crawlBitMidi',
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
        
        if args.path == None:
            print("No path provided, saving to BitMidi folder in current directory")
            args.path = os.path.join(os.getcwd(), "BitMidi")
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
            print(results)
            
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

#print(search('kesha'))