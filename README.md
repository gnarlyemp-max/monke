# Hoyolab RSS Feeds

This project generates RSS feeds for Hoyolab game announcements.

## Vercel Deployment Usage

The Vercel deployment exposes a single serverless function endpoint:

`/api/feed`

### Query Parameters

-   `game`: The game to generate a feed for.
    -   `genshin`
    -   `starrail`
    -   `honkai`
    -   `zenless`
    -   `tears_of_themis`
    -   `all` (default)
-   `format`: The format of the feed.
    -   `atom` (default)
    -   `json`
    -   `all`
-   `lang`: The language for the feed. Defaults to `en-us`. To set the language to Indonesian, use `id-id`.

### Examples

-   **Get an Atom feed for Genshin Impact in Indonesian:**
    ```
    /api/feed?game=genshin&format=atom&lang=id-id
    ```
-   **Get an Atom feed for Genshin Impact:**
    ```
    /api/feed?game=genshin&format=atom
    ```
-   **Get a JSON feed for Honkai: Star Rail:**
    ```
    /api/feed?game=starrail&format=json
    ```
-   **Get an Atom feed for Zenless Zone Zero:**
    ```
    /api/feed?game=zenless&format=atom
    ```
-   **Generate all feeds for all games:**
    ```
    /api/feed?game=all&format=all
    ```

## Local Development

To run the project locally, you'll need Python 3.11 and pip.

1.  Install the dependencies:
    ```
    pip install -r requirements.txt
    ```
2.  Run the main script:
    ```
    python main.py
