"""Teks lokalisasi bahasa Indonesia untuk aplikasi."""

MESSAGES = {
    "config_not_found": "Konfigurasi tidak ditemukan di: {path}",
    "config_created": "Konfigurasi default telah dibuat di: {path}",
    "config_created_exit": "Silakan edit file konfigurasi dan jalankan kembali aplikasi.",
    "generating_feeds": "Membuat feed RSS untuk {game}...",
    "feed_generated": "Feed RSS berhasil dibuat: {path}",
    "error_occurred": "Terjadi kesalahan: {error}",
    "fetching_news": "Mengambil berita dari Hoyolab...",
    "no_news_found": "Tidak ada berita ditemukan untuk {game}",
    "feed_collection_start": "Membuat feed RSS untuk semua game...",
    "feed_collection_complete": "Semua feed RSS berhasil dibuat!",
    "invalid_game": "Game tidak valid: {game}",
    "help_config": "Jalur ke file konfigurasi TOML",
    "help_output": "Direktori output untuk file RSS",
    "api_error": "Kesalahan saat mengambil berita: {error}",
}

GAME_NAMES = {
    "genshin": "Genshin Impact",
    "starrail": "Honkai: Star Rail",
    "honkai": "Honkai Impact 3rd",
    "zenless": "Zenless Zone Zero",
    "tears_of_themis": "Tears of Themis",
}

def get_message(key: str, **kwargs) -> str:
    """Dapatkan pesan yang telah diterjemahkan dengan parameter opsional."""
    message = MESSAGES.get(key, key)
    if kwargs:
        return message.format(**kwargs)
    return message
