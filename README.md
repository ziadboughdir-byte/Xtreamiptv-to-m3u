# IPTV to M3U Converter

A Python GUI application (PyQt6) to fetch IPTV server information, generate M3U playlists for TV, radios, and VOD (movies) from Xtream Codes-based IPTV servers, with search, edit, test, and auto-clean features.

## Features
- GUI with tabs: "Single URL" for full M3U generation and editing, "Multi Server Info" for batch server details from multiple URLs
- Fetch and display server info including total TV channels, radios, and VOD
- Generate M3U playlists for live TV, radios (with fallback keyword filtering), and VOD/movies
- Search and filter channels/stations by name
- Editable M3U preview: remove/add channels manually
- Test channel accessibility and auto-remove failed ones
- Asynchronous requests using `aiohttp` and `asyncio`
- Supports `get.php` and `player_api.php` endpoints
- Handles URLs with or without explicit port

## Clone the Repository

```bash
git clone https://github.com/ziadboughdir-byte/iptv-to-m3u.git
cd iptv-to-m3u
```

## Usage
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```
3. In "Single URL" tab: Enter URL, fetch info, generate M3U, search/edit/test/save.
4. In "Multi Server Info" tab: Paste multiple URLs (one per line), click "Fetch All Server Infos" to view batch results.

## Output
- Generates M3U content in the preview (editable).
- Save via file dialog as .m3u.
- Server info displayed in GUI.

## Example URLs
- `http://example.com:8080/player_api.php?username=USER&password=PASS`
- `http://example.com/get.php?username=USER&password=PASS&type=m3u_plus`

## Author

Developed by [ziadboughdir-byte](https://github.com/ziadboughdir-byte)

## Contributing

If you would like to contribute to this project, feel free to fork the repository and submit pull requests. Ensure that your code follows the existing structure, and test it thoroughly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
