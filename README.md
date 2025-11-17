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

### Examples

-   **Get an Atom feed for Genshin Impact:**
    ```
    /api/feed?game=genshin&format=atom
    ```
-   **Get a JSON feed for Star Rail:**
    ```
    /api/feed?game=starrail&format=json
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
