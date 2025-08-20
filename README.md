# What Should I Watch?

This is a little Flask web app that helps you figure out what movie to watch based on your region, streaming services, genre, age rating, time period, runtime, and a couple of other options.
It pulls data straight from [The Movie Database (TMDB)](https://www.themoviedb.org/) API and shows you movies with posters, grouped by provider.

## How it works
- You pick your region (like US, UK, etc.)
- You add your streaming services (autocomplete + tag selector)
- Choose a genre, rating, decade range, runtime, and whether to allow foreign films
- Decide if you want to see movies that require extra charge (rent/buy)
- The app talks to TMDB and shows you matching movies with posters

## Running it locally
You only need Python 3 and Flask installed.

1. Clone/download this repo
2. Install dependencies:
   ```bash
   pip install flask requests
