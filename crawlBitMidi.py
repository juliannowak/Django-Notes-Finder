from requests_html import HTMLSession, AsyncHTMLSession

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
    
def scrape(data: dict):
    for song in data.keys():
        midi = session.get('https://bitmidi.com/' + data[song], stream = True) 
        with open(song + '.mid', 'wb') as file:
            for chunk in midi.iter_content(chunk_size=1024):
                # writing one chunk at a time
                if chunk: 
                    file.write(chunk) 

print(search('kesha'))