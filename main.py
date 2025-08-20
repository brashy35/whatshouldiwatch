from flask import Flask, request, render_template
import requests
import datetime

API_KEY = "YOUR_API_KEY_HERE"

# telling Flask that templates live in the current directory.
app = Flask(__name__, template_folder='.')

# -------- utility functions --------

def fetch_providers_list(api_key):
    url = "https://api.themoviedb.org/3/watch/providers/movie"
    params = {"api_key": api_key, "language": "en-US"}
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json().get("results", [])

def fetch_genres(api_key):
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {"api_key": api_key, "language": "en-US"}
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json().get("genres", [])

def fetch_countries(api_key):
    url = "https://api.themoviedb.org/3/configuration/countries"
    params = {"api_key": api_key}
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json()

def discover_movies_by_filters(
        api_key, provider_id, region,
        genre_id=None, certification=None,
        date_from=None, date_to=None,
        runtime_gte=None, runtime_lte=None,
        monetization=None, orig_langs=None):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "language": "en-US",
        "with_watch_providers": provider_id,
        "watch_region": region,
        "page": 1
    }
    if genre_id:
        params["with_genres"] = genre_id
    if certification:
        params["certification_country"] = region
        params["certification.lte"] = certification
    if date_from and date_to:
        params["primary_release_date.gte"] = date_from
        params["primary_release_date.lte"] = date_to
    if runtime_gte is not None:
        params["with_runtime.gte"] = runtime_gte
    if runtime_lte is not None:
        params["with_runtime.lte"] = runtime_lte
    if monetization:
        params["with_watch_monetization_types"] = monetization
    if orig_langs is not None:
        params["with_original_language"] = "|".join(orig_langs)
    res = requests.get(url, params=params)
    res.raise_for_status()
    return res.json().get("results", [])

# -------- routes --------

@app.route('/', methods=['GET', 'POST'])
def index():
    providers = fetch_providers_list(API_KEY)
    genres = fetch_genres(API_KEY)
    countries = fetch_countries(API_KEY)

    now = datetime.datetime.now().year
    current_decade = now // 10 * 10
    decades = list(range(1900, current_decade + 1, 10))

    runtime_ranges = [
        ("<60 min (<1h)", None, 59),
        ("60-90 min (1h-1.5h)", 60, 90),
        ("90-120 min (1.5h-2h)", 90, 120),
        ("120-180 min (2h-3h)", 120, 180),
        (">180 min (>3h)", 181, None)
    ]

    results = None

    if request.method == 'POST':
        region = request.form.get('region')
        selected_pids = request.form.getlist('services')
        genre_id = request.form.get('genre') or None
        certification = request.form.get('rating') or None

        start_dec = request.form.get('start_decade')
        end_dec = request.form.get('end_decade')
        date_from = f"{start_dec}-01-01" if start_dec else None
        date_to = f"{int(end_dec)+9}-12-31" if end_dec else None

        sel_range = request.form.get('runtime_range')
        runtime_gte, runtime_lte = None, None
        for label, gte, lte in runtime_ranges:
            if label == sel_range:
                runtime_gte, runtime_lte = gte, lte
                break

        paid = request.form.get('pay_extra') == 'on'
        monetization = None if paid else "flatrate|free|ads"

        include_foreign = request.form.get('include_foreign') == 'on'
        orig_langs = None if include_foreign else ['en']

        results = {}
        for prov in providers:
            pid = str(prov.get('provider_id'))
            if pid in selected_pids:
                movies = discover_movies_by_filters(
                    API_KEY, pid, region,
                    genre_id=genre_id,
                    certification=certification,
                    date_from=date_from, date_to=date_to,
                    runtime_gte=runtime_gte, runtime_lte=runtime_lte,
                    monetization=monetization,
                    orig_langs=orig_langs
                )
                results[prov.get('provider_name')] = movies

    return render_template(
        'index.html',
        providers=providers,
        genres=genres,
        countries=countries,
        decades=decades,
        runtime_ranges=runtime_ranges,
        results=results
    )

if __name__ == '__main__':
    app.run(debug=True)
