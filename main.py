import sys
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTextEdit, QLabel, QFileDialog, QProgressBar,
                             QMessageBox)
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QFont
from iptv_client import IPTVClient
from config_manager import CONFIG


class Worker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.func(*self.args, **self.kwargs))
            loop.close()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MultiInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Multi URL input
        url_label = QLabel("🔗 Multiple URLs (one per line):")
        url_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(url_label)
        self.multi_urls = QTextEdit()
        self.multi_urls.setPlaceholderText("Paste multiple IPTV URLs here, one per line (get.php will be converted to player_api.php)...")
        self.multi_urls.setMaximumHeight(100)
        layout.addWidget(self.multi_urls)

        # Buttons
        btn_layout = QHBoxLayout()
        self.multi_fetch_btn = QPushButton("🔍 Fetch All Server Infos")
        self.multi_fetch_btn.clicked.connect(self.fetch_multi_info)
        btn_layout.addWidget(self.multi_fetch_btn)

        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

        # Multi results
        results_label = QLabel("📊 Server Infos:")
        results_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(results_label)
        self.multi_results = QTextEdit()
        self.multi_results.setReadOnly(True)
        layout.addWidget(self.multi_results)

        self.multi_client = None

    def clear_all(self):
        self.multi_urls.clear()
        self.multi_results.clear()

    def clean_url(self, url_str):
        """Clean and convert URL to player_api.php format, handling direct stream URLs."""
        if not url_str or url_str.strip().lower() in ['m3u', '']:
            return None
        url = url_str.strip()
        from urllib.parse import urlparse, urlunparse, parse_qs

        parsed = urlparse(url)
        username = None
        password = None

        if len(parsed.path.split('/')) >= 4 and not 'get.php' in url and not 'player_api.php' in url:
            # Assume direct stream format: /username/password/id
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) >= 3:
                username = path_parts[-3]
                password = path_parts[-2]
                # Reconstruct base URL
                host_port = f"{parsed.scheme}://{parsed.netloc}"
                # Construct player_api URL with username/password
                url = f"{host_port}/player_api.php?username={username}&password={password}"
        elif 'get.php' in url or 'player_api.php' in url:
            # Extract from query
            query = parse_qs(parsed.query)
            username = query.get('username', [None])[0]
            password = query.get('password', [None])[0]
            if username and password:
                host_port = f"{parsed.scheme}://{parsed.netloc}"
                # Ensure player_api format
                if 'get.php' in url:
                    url = f"{host_port}/player_api.php?username={username}&password={password}"
                else:
                    url = f"{host_port}/player_api.php?username={username}&password={password}"
            else:
                return None
        else:
            # Standard URL with query
            username = parsed.username or parse_qs(parsed.query).get('username', [None])[0]
            password = parsed.password or parse_qs(parsed.query).get('password', [None])[0]
            if username and password:
                host_port = f"{parsed.scheme}://{parsed.netloc}"
                url = f"{host_port}/player_api.php?username={username}&password={password}"
            else:
                return None

        return url if username and password and url.startswith(('http://', 'https://')) else None

    def fetch_multi_info(self):
        urls_text = self.multi_urls.toPlainText().strip()
        if not urls_text:
            self.multi_results.setText("Please enter URLs.")
            return

        raw_urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        cleaned_urls = []
        for raw in raw_urls:
            clean = self.clean_url(raw)
            if clean:
                cleaned_urls.append(clean)
            else:
                self.multi_results.append(f"Skipped invalid: {raw}")

        if not cleaned_urls:
            self.multi_results.setText("No valid URLs found after cleaning.")
            return

        self.multi_fetch_btn.setEnabled(False)
        self.worker = Worker(self._fetch_multi_async, cleaned_urls)
        self.worker.finished.connect(self._on_multi_finished)
        self.worker.error.connect(self._on_multi_error)
        self.worker.start()

    async def _fetch_multi_async(self, urls):
        results = {}
        for url in urls:
            try:
                client = IPTVClient(url)
                info = await client.get_server_info()
                results[url] = info
            except Exception as e:
                results[url] = {"error": str(e)}
        return results

    def _on_multi_finished(self, results):
        self.multi_fetch_btn.setEnabled(True)
        output = ""
        for url, info in results.items():
            output += f"\n--- {url} ---\n"
            if "error" in info:
                output += f"Error: {info['error']}\n"
            else:
                display_info = {k: v for k, v in info.items() if k != "password"}
                output += "\n".join([f"{k}: {v}" for k, v in display_info.items()]) + "\n"
        self.multi_results.setText(output.strip())

    def _on_multi_error(self, err):
        self.multi_fetch_btn.setEnabled(True)
        self.multi_results.setText(f"Error: {err}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPTV to M3U Converter")
        
        # Utiliser les dimensions de fenêtre depuis la configuration
        window_width = CONFIG.get('ui', 'window_width', 1000)
        window_height = CONFIG.get('ui', 'window_height', 700)
        self.setGeometry(100, 100, window_width, window_height)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Single URL Tab
        self.single_tab = QWidget()
        self.tabs.addTab(self.single_tab, "Single URL")
        single_layout = QVBoxLayout(self.single_tab)
        single_layout.setSpacing(10)
        single_layout.setContentsMargins(20, 20, 20, 20)

        # Logo/Title with emoji
        title_label = QLabel("📺 IPTV to M3U Converter")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        single_layout.addWidget(title_label)


        # URL input section
        url_layout = QHBoxLayout()
        url_label = QLabel("🔗 URL:")
        url_label.setFont(QFont("", 12, QFont.Weight.Bold))
        url_layout.addWidget(url_label)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter IPTV URL (e.g., http://host:port/get.php?username=...&password=...)")
        url_layout.addWidget(self.url_input)
        single_layout.addLayout(url_layout)

        # Fetch info button
        self.fetch_btn = QPushButton("🔍 Fetch Server Info")
        self.fetch_btn.clicked.connect(self.fetch_info)
        single_layout.addWidget(self.fetch_btn)

        # Info display
        info_label = QLabel("📊 Server Info:")
        info_label.setFont(QFont("", 12, QFont.Weight.Bold))
        single_layout.addWidget(info_label)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        single_layout.addWidget(self.info_text)

        # Generate M3U buttons
        gen_layout = QHBoxLayout()
        self.generate_btn = QPushButton("📺 Generate TV M3U")
        self.generate_btn.clicked.connect(self.generate_m3u)
        gen_layout.addWidget(self.generate_btn)

        self.radio_btn = QPushButton("📻 Generate Radio M3U")
        self.radio_btn.clicked.connect(self.generate_radio)
        gen_layout.addWidget(self.radio_btn)

        self.vod_btn = QPushButton("🎥 Generate VOD M3U")
        self.vod_btn.clicked.connect(self.generate_vod)
        gen_layout.addWidget(self.vod_btn)

        single_layout.addLayout(gen_layout)

        # M3U preview
        m3u_label = QLabel("📄 M3U Preview:")
        m3u_label.setFont(QFont("", 12, QFont.Weight.Bold))
        single_layout.addWidget(m3u_label)

        # Search input for M3U
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Search:")
        search_label.setFont(QFont("", 10))
        search_layout.addWidget(search_label)
        self.m3u_search = QLineEdit()
        self.m3u_search.setPlaceholderText("Search channels by name...")
        self.m3u_search.textChanged.connect(self.filter_m3u)
        search_layout.addWidget(self.m3u_search)
        single_layout.addLayout(search_layout)

        self.m3u_text = QTextEdit()
        self.m3u_text.setReadOnly(True)
        self.m3u_text.setMaximumHeight(300)
        single_layout.addWidget(self.m3u_text)

        # Save button
        self.save_btn = QPushButton("💾 Save M3U")
        self.save_btn.clicked.connect(self.save_m3u)
        single_layout.addWidget(self.save_btn)

        # Test channels button
        self.test_btn = QPushButton("✅ Test Channels")
        self.test_btn.clicked.connect(self.test_channels)
        self.test_btn.setEnabled(False)
        single_layout.addWidget(self.test_btn)

        # Remove failed channels button
        self.remove_btn = QPushButton("🗑️ Remove Failed Channels")
        self.remove_btn.clicked.connect(self.remove_failed)
        self.remove_btn.setEnabled(False)
        single_layout.addWidget(self.remove_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        single_layout.addWidget(self.progress_bar)

        # Test results
        test_label = QLabel("📈 Channel Test Results:")
        test_label.setFont(QFont("", 12, QFont.Weight.Bold))
        single_layout.addWidget(test_label)
        self.test_results = QLabel("No test performed yet.")
        self.test_results.setStyleSheet("background-color: #3c3c3c; border: 1px solid #555; border-radius: 5px; padding: 10px;")
        self.test_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
        single_layout.addWidget(self.test_results)

        # Multi Info Tab
        self.multi_tab = MultiInfoTab()
        self.tabs.addTab(self.multi_tab, "Multi Server Info")

        # About Tab
        self.about_tab = QWidget()
        self.tabs.addTab(self.about_tab, "About")
        about_layout = QVBoxLayout(self.about_tab)
        about_layout.setSpacing(20)
        about_layout.setContentsMargins(20, 20, 20, 20)

        # Developer info
        dev_label = QLabel("👨‍💻 Developer: ZiadBoughdir")
        dev_label.setFont(QFont("", 14, QFont.Weight.Bold))
        dev_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(dev_label)

        # GitHub link
        github_label = QLabel('<a href="https://github.com/ziadboughdir-byte" style="color: #007acc;">🔗 GitHub Repository</a>')
        github_label.setOpenExternalLinks(True)
        github_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        github_label.setFont(QFont("", 12))
        about_layout.addWidget(github_label)

        # Version info
        version_label = QLabel("📦 Version: 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(QFont("", 12))
        about_layout.addWidget(version_label)

        about_layout.addStretch()  # Push content to top

        self.m3u_content = ""
        self.m3u_lines = []
        self.working_urls = set()
        self.client = None

    def fetch_info(self):
        url = self.url_input.text().strip()
        if not url:
            self.info_text.setText("Please enter a URL.")
            return

        self.fetch_btn.setEnabled(False)
        self.worker = Worker(self._fetch_info_async, url, use_cache=True)
        self.worker.finished.connect(self._on_fetch_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    async def _fetch_info_async(self, url, use_cache=True):
        self.client = IPTVClient(url, use_cache=use_cache)
        info = await self.client.get_server_info()
        return info

    def _on_fetch_finished(self, result):
        self.fetch_btn.setEnabled(True)
        if isinstance(result, dict):
            # Hide password in display
            display_info = {k: v for k, v in result.items() if k != "password"}
            info_str = "\n".join([f"{k}: {v}" for k, v in display_info.items()])
            self.info_text.setText(info_str)
        else:
            self.info_text.setText("No info retrieved.")

    def generate_m3u(self):
        url = self.url_input.text().strip()
        if not url:
            self.m3u_text.setText("Please enter a URL.")
            return

        self.generate_btn.setEnabled(False)
        self.radio_btn.setEnabled(False)
        self.worker = Worker(self._generate_async, url, use_cache=True)
        self.worker.finished.connect(self._on_generate_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    async def _generate_async(self, url, use_cache=True):
        self.client = IPTVClient(url, use_cache=use_cache)
        return await self.client.generate_m3u()

    def generate_radio(self):
        url = self.url_input.text().strip()
        if not url:
            self.m3u_text.setText("Please enter a URL.")
            return

        self.radio_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.vod_btn.setEnabled(False)
        self.worker = Worker(self._generate_radio_async, url, use_cache=True)
        self.worker.finished.connect(self._on_generate_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    async def _generate_radio_async(self, url, use_cache=True):
        self.client = IPTVClient(url, use_cache=use_cache)
        return await self.client.generate_radio_m3u()

    def generate_vod(self):
        url = self.url_input.text().strip()
        if not url:
            self.m3u_text.setText("Please enter a URL.")
            return

        self.vod_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.radio_btn.setEnabled(False)
        self.worker = Worker(self._generate_vod_async, url, use_cache=True)
        self.worker.finished.connect(self._on_generate_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    async def _generate_vod_async(self, url, use_cache=True):
        self.client = IPTVClient(url, use_cache=use_cache)
        return await self.client.generate_vod_m3u()

    def _on_generate_finished(self, content):
        self.generate_btn.setEnabled(True)
        self.radio_btn.setEnabled(True)
        self.vod_btn.setEnabled(True)
        if content:
            self.m3u_content = content
            self.m3u_lines = content.split('\n')
            self.filter_m3u()
            self.m3u_text.setReadOnly(False)
            self.test_btn.setEnabled(True)
        else:
            self.m3u_text.setText("No M3U content generated.")
            self.m3u_text.setReadOnly(True)
            self.m3u_lines = []

    def test_channels(self):
        if not self.m3u_content:
            self.test_results.setText("Generate M3U first.")
            return

        self.test_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.worker = Worker(self._test_async, self.m3u_content)
        self.worker.finished.connect(self._on_test_finished)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()

    async def _test_async(self, m3u_content):
        if not self.client:
            url = self.url_input.text().strip()
            self.client = IPTVClient(url, use_cache=True)
        return await self.client.test_channels(m3u_content)

    def _on_test_finished(self, results):
        self.test_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        if isinstance(results, dict):
            total = results.get('total', 0)
            working = results.get('working', 0)
            failed = results.get('failed', 0)
            self.working_urls = results.get('working_urls', set())
            self.test_results.setText(f"Total: {total}, Working: {working}, Failed: {failed}")
        else:
            self.test_results.setText("Test failed.")
            self.working_urls = set()

    def filter_m3u(self):
        search_text = self.m3u_search.text().lower().strip()
        if not self.m3u_lines:
            return

        filtered_lines = []
        i = 0
        while i < len(self.m3u_lines):
            line = self.m3u_lines[i].strip()
            if line.startswith('#EXTINF:'):
                # Extract channel name (after comma)
                if ',' in line:
                    channel_name = line.split(',', 1)[1].strip().lower()
                    if not search_text or search_text in channel_name:
                        # Include this EXTINF and the next line (URL)
                        filtered_lines.append(self.m3u_lines[i])
                        if i + 1 < len(self.m3u_lines):
                            filtered_lines.append(self.m3u_lines[i + 1])
            i += 1

        preview = '\n'.join(filtered_lines)
        self.m3u_text.setText(preview)

    def remove_failed(self):
        if not self.m3u_lines or not self.working_urls:
            self.test_results.setText("Test channels first.")
            return

        new_lines = ["#EXTM3U"]
        i = 0
        while i < len(self.m3u_lines):
            line = self.m3u_lines[i].strip()
            if line.startswith('#EXTINF:'):
                if i + 1 < len(self.m3u_lines):
                    url = self.m3u_lines[i + 1].strip()
                    if url in self.working_urls:
                        new_lines.append(self.m3u_lines[i])
                        new_lines.append(self.m3u_lines[i + 1])
            i += 1

        self.m3u_lines = new_lines
        self.m3u_content = '\n'.join(new_lines)
        self.filter_m3u()
        self.remove_btn.setEnabled(False)
        self.test_results.setText(f"Removed failed channels. New total: {len(self.working_urls)}")


    def save_m3u(self):
        edited_content = self.m3u_text.toPlainText().strip()
        if not edited_content:
            self.m3u_text.setText("No M3U content to save. Generate first.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Save M3U", "playlist.m3u", "M3U Files (*.m3u)"
        )
        if filename:
            try:
                if not self.client:
                    url = self.url_input.text().strip()
                    self.client = IPTVClient(url)
                saved_filename = self.client.save_m3u(edited_content, filename)
                self.m3u_text.append(f"\nSaved to: {saved_filename}")
            except Exception as e:
                self.m3u_text.setText(f"Error saving: {e}")

    def _on_error(self, err):
        self.fetch_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.radio_btn.setEnabled(True)
        self.vod_btn.setEnabled(True)
        self.remove_btn.setEnabled(False)
        self.info_text.setText(f"Error: {err}")
        self.m3u_text.setText("")
        self.m3u_text.setReadOnly(True)
        self.working_urls = set()


def main():
    app = QApplication(sys.argv)

    # Apply original simple styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Segoe UI', Arial;
        }
        QLineEdit {
            background-color: #3c3c3c;
            border: 1px solid #555;
            border-radius: 5px;
            padding: 8px;
            color: #ffffff;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #007acc;
        }
        QPushButton {
            background-color: #007acc;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QPushButton:pressed {
            background-color: #004080;
        }
        QPushButton:disabled {
            background-color: #555;
            color: #888;
        }
        QTextEdit {
            background-color: #3c3c3c;
            border: 1px solid #555;
            border-radius: 5px;
            padding: 8px;
            color: #ffffff;
            font-size: 12px;
        }
        QLabel {
            color: #ffffff;
            font-size: 12px;
            font-weight: bold;
            padding: 5px;
        }
        QProgressBar {
            border: 1px solid #555;
            border-radius: 5px;
            text-align: center;
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QProgressBar::chunk {
            background-color: #007acc;
            border-radius: 4px;
        }
        QTabWidget::pane {
            border: 1px solid #555;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #555;
            padding: 8px 16px;
            margin-right: 2px;
            border-radius: 4px 4px 0 0;
        }
        QTabBar::tab:selected {
            background-color: #007acc;
            color: #ffffff;
        }
        QTabBar::tab:hover {
            background-color: #005a9e;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
