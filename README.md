# Django-Notes-Finder
a couple of crawlers to scrape the internet for MIDI files, to then convert into PDF sheet music, and hosts both. Give the music back to the people!  

# TODO
- fix crawlers: duplicate file extensions
- Playwright support / make requests-html the lightweight alternative.
- upload midi file on front page
- Lilypond PDF generation with Celery and asynchoronize other subprocesses
- dockerize it
- pick another SASS theme and style the website
- host it... coming soon tm
- change transpose to be a +/- integer rather than note letter

# LAYOUT
- search and upload -> results (links for each, to midi and sheet) -> a preview, transpose, download for each