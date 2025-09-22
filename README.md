# IPTV to M3U Converter

A Python GUI application (PyQt6) to fetch IPTV server information, generate M3U playlists for TV, radios, and VOD (movies) from Xtream Codes-based IPTV servers, with search, edit, test, and auto-clean features.

## Features
- GUI interface with PyQt6 for easy use
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
3. Enter your IPTV URL in the GUI (e.g., http://host:port/player_api.php?username=USER&password=PASS).
4. Click "Fetch Server Info" to view details.
5. Click "Generate TV M3U", "Generate Radio M3U", or "Generate VOD M3U" to create playlists.
6. Use search to filter, edit the preview, test channels, remove failed, and save.

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
