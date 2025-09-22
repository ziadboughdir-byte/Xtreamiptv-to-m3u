import sys
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTextEdit, QLabel, QFileDialog, QProgressBar)
from PyQt6.QtCore import pyqtSignal, QThread, Qt
from PyQt6.QtGui import QFont
from iptv_client import IPTVClient


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPTV to M3U Converter")
        self.setGeometry(100, 100, 800, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo/Title with emoji
        title_label = QLabel("📺 IPTV to M3U Converter")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # URL input section
        url_layout = QHBoxLayout()
        url_label = QLabel("🔗 URL:")
        url_label.setFont(QFont("", 12, QFont.Weight.Bold))
        url_layout.addWidget(url_label)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter IPTV URL (e.g., http://host:port/get.php?username=...&password=...)")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Fetch info button
        self.fetch_btn = QPushButton("🔍 Fetch Server Info")
        self.fetch_btn.clicked.connect(self.fetch_info)
        layout.addWidget(self.fetch_btn)

        # Info display
        info_label = QLabel("📊 Server Info:")
        info_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(info_label)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)

        # Generate M3U buttons
        gen_layout = QHBoxLayout()
        self.generate_btn = QPushButton("📺 Generate TV M3U")
        self.generate_btn.clicked.connect(self.generate_m3u)
        gen_layout.addWidget(self.generate_btn)

        self.radio_btn = QPushButton("📻 Generate Radio M3U")
        self.radio_btn.clicked.connect(self.generate_radio)
        gen_layout.addWidget(self.radio_btn)

        layout.addLayout(gen_layout)

        # M3U preview
        m3u_label = QLabel("📄 M3U Preview:")
        m3u_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(m3u_label)

        # Search input for M3U
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Search:")
        search_label.setFont(QFont("", 10))
        search_layout.addWidget(search_label)
        self.m3u_search = QLineEdit()
        self.m3u_search.setPlaceholderText("Search channels by name...")
        self.m3u_search.textChanged.connect(self.filter_m3u)
        search_layout.addWidget(self.m3u_search)
        layout.addLayout(search_layout)

        self.m3u_text = QTextEdit()
        self.m3u_text.setReadOnly(True)
        self.m3u_text.setMaximumHeight(300)
        layout.addWidget(self.m3u_text)

        # Save button
        self.save_btn = QPushButton("💾 Save M3U")
        self.save_btn.clicked.connect(self.save_m3u)
        layout.addWidget(self.save_btn)

        # Test channels button
        self.test_btn = QPushButton("✅ Test Channels")
        self.test_btn.clicked.connect(self.test_channels)
        self.test_btn.setEnabled(False)
        layout.addWidget(self.test_btn)

        # Remove failed channels button
        self.remove_btn = QPushButton("🗑️ Remove Failed Channels")
        self.remove_btn.clicked.connect(self.remove_failed)
        self.remove_btn.setEnabled(False)
        layout.addWidget(self.remove_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Test results
        test_label = QLabel("📈 Channel Test Results:")
        test_label.setFont(QFont("", 12, QFont.Weight.Bold))
        layout.addWidget(test_label)
        self.test_results = QLabel("No test performed yet.")
        self.test_results.setStyleSheet("background-color: #3c3c3c; border: 1px solid #555; border-radius: 5px; padding: 10px;")
        self.test_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.test_results)

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
        self.worker = Worker(self._fetch_info_async, url)
        self.worker.finished.connect(self._on_fetch_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    async def _fetch_info_async(self, url):
        self.client = IPTVClient(url)
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
        self.worker = Worker(self._generate_async, url)
        self.worker.finished.connect(self._on_generate_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    async def _generate_async(self, url):
        self.client = IPTVClient(url)
        return await self.client.generate_m3u()

    def generate_radio(self):
        url = self.url_input.text().strip()
        if not url:
            self.m3u_text.setText("Please enter a URL.")
            return

        self.radio_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.worker = Worker(self._generate_radio_async, url)
        self.worker.finished.connect(self._on_generate_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    async def _generate_radio_async(self, url):
        self.client = IPTVClient(url)
        return await self.client.generate_radio_m3u()

    def _on_generate_finished(self, content):
        self.generate_btn.setEnabled(True)
        self.radio_btn.setEnabled(True)
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
        self.worker = Worker(self._test_async)
        self.worker.finished.connect(self._on_test_finished)
        self.worker.error.connect(self._on_error)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.start()

    async def _test_async(self):
        if not self.client:
            url = self.url_input.text().strip()
            self.client = IPTVClient(url)
        return await self.client.test_channels(self.m3u_content)

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
        self.remove_btn.setEnabled(False)
        self.info_text.setText(f"Error: {err}")
        self.m3u_text.setText("")
        self.m3u_text.setReadOnly(True)
        self.working_urls = set()


def main():
    app = QApplication(sys.argv)
    
    # Apply global stylesheet for theme
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
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
