import asyncio
import aiohttp
from urllib.parse import urlparse, parse_qs
import json
import platform
import datetime
from typing import Optional, Tuple, Dict, List, Any

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class IPTVClient:
    def __init__(self, url: str):
        self.url = url
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.scheme: str = "http"

    def parse_url(self) -> Tuple[Optional[str], Optional[int], Optional[str], Optional[str]]:
        """Parse URL to extract host, port, username, password."""
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL format. Must start with 'http://' or 'https://'.")
        
        parsed = urlparse(self.url)
        self.scheme = parsed.scheme
        self.host = parsed.hostname
        if not self.host:
            raise ValueError("Invalid host in URL.")
        
        self.port = parsed.port
        if not self.port:
            self.port = 443 if self.scheme == "https" else 80
        
        self.username = parsed.username
        self.password = parsed.password
        
        if not self.username or not self.password:
            qs = parse_qs(parsed.query)
            self.username = self.username or qs.get("username", [None])[0]
            self.password = self.password or qs.get("password", [None])[0]
        
        if not self.username or not self.password:
            raise ValueError("Username and password must be provided in URL or query params.")
        
        return self.host, self.port, self.username, self.password

    def construct_base_url(self) -> str:
        """Construct base URL for requests."""
        port_str = f":{self.port}" if self.port != (443 if self.scheme == "https" else 80) else ""
        return f"{self.scheme}://{self.host}{port_str}"

    async def fetch(self, session: aiohttp.ClientSession, url: str, method: str = "GET", 
                    data: Optional[Dict] = None, headers: Optional[Dict] = None) -> str:
        """Perform async HTTP request."""
        default_headers = {
            "Accept": "*/*",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 14; 22101320G Build/UKQ1.231003.002)",
            "Accept-Language": "en-US,en;q=0.5",
        }
        if headers:
            default_headers.update(headers)
        
        try:
            async with session.request(method, url, data=data, headers=default_headers) as resp:
                resp.raise_for_status()
                return await resp.text()
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed: {e}")

    async def get_server_info(self) -> Dict[str, Any]:
        """Fetch and parse server/user info."""
        self.parse_url()
        base_url = self.construct_base_url()
        api_url = f"{base_url}/player_api.php?username={self.username}&password={self.password}"
        
        headers = {"Referer": base_url, "Host": self.host}
        
        async with aiohttp.ClientSession() as session:
            resp_text = await self.fetch(session, api_url, headers=headers)
            try:
                info = json.loads(resp_text)
                user_info = info.get("user_info", {})
                server_info = info.get("server_info", {})
                
                max_connections = user_info.get("max_connections", "Unlimited") or "Unlimited"
                active_connections = user_info.get("active_cons", 0)
                trial = "Yes" if user_info.get("is_trial") == "1" else "No"
                expire = user_info.get("exp_date", "Unlimited")
                if expire and expire != "Unlimited":
                    try:
                        expire = datetime.datetime.fromtimestamp(int(expire)).strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        expire = "Invalid"
                status = user_info.get("status", "Unknown")
                
                # Fetch total live channels
                streams_url = f"{base_url}/player_api.php?username={self.username}&password={self.password}&action=get_live_streams"
                streams_resp = await self.fetch(session, streams_url, headers=headers)
                streams = json.loads(streams_resp) if streams_resp else []
                total_channels = len(streams) if isinstance(streams, list) else 0

                # Fetch total radios
                radios_url = f"{base_url}/player_api.php?username={self.username}&password={self.password}&action=get_radio_streams"
                radios_resp = await self.fetch(session, radios_url, headers=headers)
                radios = json.loads(radios_resp) if radios_resp else []
                total_radios = len(radios) if isinstance(radios, list) else 0

                # Fetch total VOD
                vod_url = f"{base_url}/player_api.php?username={self.username}&password={self.password}&action=get_vod_streams"
                vod_resp = await self.fetch(session, vod_url, headers=headers)
                vods = json.loads(vod_resp) if vod_resp else []
                total_vod = len(vods) if isinstance(vods, list) else 0
                
                return {
                    "host": f"{self.scheme}://{self.host}:{self.port}" if self.port != (443 if self.scheme == "https" else 80) else f"{self.scheme}://{self.host}",
                    "username": self.username,
                    "password": self.password,  # Note: In real app, don't expose password
                    "m3u_url": f"{base_url}/get.php?username={self.username}&password={self.password}&type=m3u_plus",
                    "max_connections": max_connections,
                    "active_connections": active_connections,
                    "trial": trial,
                    "status": status,
                    "expire": expire,
                    "total_channels": total_channels,
                    "total_radios": total_radios,
                    "total_vod": total_vod
                }
            except json.JSONDecodeError as e:
                raise Exception(f"Failed to parse server info: {e}")

    async def generate_m3u(self) -> str:
        """Generate M3U playlist content for live TV."""
        self.parse_url()
        base_url = self.construct_base_url()
        
        headers = {"Referer": base_url, "Host": self.host}
        
        async with aiohttp.ClientSession() as session:
            # Get categories
            cat_data = {
                "username": self.username,
                "password": self.password,
                "action": "get_live_categories"
            }
            cat_headers = headers.copy()
            cat_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
            
            cat_url = f"{base_url}/player_api.php"
            cat_resp = await self.fetch(session, cat_url, "POST", cat_data, cat_headers)
            categories = json.loads(cat_resp)
            cat_map = {c["category_id"]: c["category_name"] for c in categories if "category_id" in c and "category_name" in c}
            
            # Get streams
            stream_data = {
                "username": self.username,
                "password": self.password,
                "action": "get_live_streams"
            }
            stream_resp = await self.fetch(session, cat_url, "POST", stream_data, cat_headers)
            streams = json.loads(stream_resp)
            
            m3u_lines = ["#EXTM3U"]
            for stream in streams:
                if not isinstance(stream, dict):
                    continue
                cat_id = str(stream.get("category_id", ""))
                cat_name = cat_map.get(cat_id, "Unknown")
                stream_icon = stream.get("stream_icon", "")
                name = stream.get("name", "")
                stream_id = stream.get("stream_id", "")
                
                if not (name and stream_id):
                    continue
                
                m3u_lines.append(f'#EXTINF:-1 tvg-logo="{stream_icon}" group-title="{cat_name}",{name}')
                stream_url = f"{base_url}/live/{self.username}/{self.password}/{stream_id}.ts"
                m3u_lines.append(stream_url)
            
            return "\n".join(m3u_lines)

    async def generate_radio_m3u(self) -> str:
        """Generate M3U playlist content for radios."""
        self.parse_url()
        base_url = self.construct_base_url()
        
        headers = {"Referer": base_url, "Host": self.host}
        
        async with aiohttp.ClientSession() as session:
            # Try dedicated radio endpoints first
            try:
                # Get radio categories
                cat_data = {
                    "username": self.username,
                    "password": self.password,
                    "action": "get_radio_categories"
                }
                cat_headers = headers.copy()
                cat_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
                
                cat_url = f"{base_url}/player_api.php"
                cat_resp = await self.fetch(session, cat_url, "POST", cat_data, cat_headers)
                categories = json.loads(cat_resp)
                cat_map = {c["category_id"]: c["category_name"] for c in categories if "category_id" in c and "category_name" in c}
                
                # Get radios
                radio_data = {
                    "username": self.username,
                    "password": self.password,
                    "action": "get_radio_streams"
                }
                radio_resp = await self.fetch(session, cat_url, "POST", radio_data, cat_headers)
                radios = json.loads(radio_resp)
                
                if radios and isinstance(radios, list) and len(radios) > 0:
                    # Use dedicated radios
                    m3u_lines = ["#EXTM3U"]
                    for radio in radios:
                        if not isinstance(radio, dict):
                            continue
                        cat_id = str(radio.get("category_id", ""))
                        cat_name = cat_map.get(cat_id, "Unknown")
                        stream_icon = radio.get("stream_icon", "")
                        name = radio.get("name", "")
                        stream_id = radio.get("id", "")  # Radios use 'id' instead of 'stream_id'
                        
                        if not (name and stream_id):
                            continue
                        
                        m3u_lines.append(f'#EXTINF:-1 tvg-logo="{stream_icon}" group-title="{cat_name}",{name}')
                        radio_url = f"{base_url}/radio/{self.username}/{self.password}/{stream_id}.ts"
                        m3u_lines.append(radio_url)
                    
                    return "\n".join(m3u_lines)
            except Exception:
                # Fallback to filtering live streams if dedicated fails or empty
                pass
            
            # Fallback: Filter live streams by radio keywords
            # Get live categories
            cat_data = {
                "username": self.username,
                "password": self.password,
                "action": "get_live_categories"
            }
            cat_headers = headers.copy()
            cat_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
            
            cat_resp = await self.fetch(session, cat_url, "POST", cat_data, cat_headers)
            categories = json.loads(cat_resp)
            cat_map = {c["category_id"]: c["category_name"] for c in categories if "category_id" in c and "category_name" in c}
            
            # Get live streams
            stream_data = {
                "username": self.username,
                "password": self.password,
                "action": "get_live_streams"
            }
            stream_resp = await self.fetch(session, cat_url, "POST", stream_data, cat_headers)
            streams = json.loads(stream_resp)
            
            radio_keywords = ["radio", "radiostation", "station", "fm", "am", "radiostations"]
            
            m3u_lines = ["#EXTM3U"]
            for stream in streams:
                if not isinstance(stream, dict):
                    continue
                name = stream.get("name", "").lower()
                if any(keyword in name for keyword in radio_keywords):
                    cat_id = str(stream.get("category_id", ""))
                    cat_name = cat_map.get(cat_id, "Unknown")
                    stream_icon = stream.get("stream_icon", "")
                    stream_id = stream.get("stream_id", "")
                    
                    if not (name and stream_id):
                        continue
                    
                    m3u_lines.append(f'#EXTINF:-1 tvg-logo="{stream_icon}" group-title="{cat_name}",{name}')
                    stream_url = f"{base_url}/live/{self.username}/{self.password}/{stream_id}.ts"
                    m3u_lines.append(stream_url)
            
            return "\n".join(m3u_lines)

    async def generate_vod_m3u(self) -> str:
        """Generate M3U playlist content for VOD (movies)."""
        self.parse_url()
        base_url = self.construct_base_url()
        
        headers = {"Referer": base_url, "Host": self.host}
        
        async with aiohttp.ClientSession() as session:
            # Get VOD categories
            cat_data = {
                "username": self.username,
                "password": self.password,
                "action": "get_vod_categories"
            }
            cat_headers = headers.copy()
            cat_headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
            
            cat_url = f"{base_url}/player_api.php"
            cat_resp = await self.fetch(session, cat_url, "POST", cat_data, cat_headers)
            categories = json.loads(cat_resp)
            cat_map = {c["category_id"]: c["category_name"] for c in categories if "category_id" in c and "category_name" in c}
            
            # Get VOD streams
            vod_data = {
                "username": self.username,
                "password": self.password,
                "action": "get_vod_streams"
            }
            vod_resp = await self.fetch(session, cat_url, "POST", vod_data, cat_headers)
            vods = json.loads(vod_resp)
            
            m3u_lines = ["#EXTM3U"]
            for vod in vods:
                if not isinstance(vod, dict):
                    continue
                cat_id = str(vod.get("category_id", ""))
                cat_name = cat_map.get(cat_id, "Unknown")
                stream_icon = vod.get("stream_icon", "")
                name = vod.get("name", "")
                stream_id = vod.get("stream_id", "")
                
                if not (name and stream_id):
                    continue
                
                m3u_lines.append(f'#EXTINF:-1 tvg-logo="{stream_icon}" group-title="{cat_name}",{name}')
                vod_url = f"{base_url}/movie/{self.username}/{self.password}/{stream_id}.mp4"
                m3u_lines.append(vod_url)
            
            return "\n".join(m3u_lines)

    def save_m3u(self, content: str, filename: Optional[str] = None) -> str:
        """Save M3U content to file."""
        self.parse_url()
        if not content:
            raise ValueError("No content to save.")
        
        if not filename:
            userpass = f"_{self.username}_{self.password}" if self.username and self.password else ""
            filename = f"{self.host}{userpass}.m3u".replace(":", "_").replace("/", "_").replace("?", "_")
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filename

    async def test_channels(self, m3u_content: str) -> dict:
        """Test accessibility of channels in M3U content."""
        self.parse_url()
        base_url = self.construct_base_url()
        
        # Parse M3U to extract stream URLs (every even line after #EXTINF)
        lines = m3u_content.strip().split('\n')
        stream_urls = []
        i = 0
        while i < len(lines):
            if lines[i].startswith('#EXTINF'):
                if i + 1 < len(lines):
                    stream_url = lines[i + 1].strip()
                    if stream_url.startswith('http'):
                        stream_urls.append(stream_url)
            i += 1
        
        total = len(stream_urls)
        if total == 0:
            return {'total': 0, 'working': 0, 'failed': 0, 'working_urls': set()}
        
        working_urls = set()
        working = 0
        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 14; 22101320G Build/UKQ1.231003.002)"}
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in stream_urls:
                # Use HEAD to check accessibility quickly
                task = self._test_single_channel(session, url, headers)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    continue
                if result:
                    working += 1
                    working_urls.add(stream_urls[idx])
        
        failed = total - working
        return {'total': total, 'working': working, 'failed': failed, 'working_urls': working_urls}
    
    async def _test_single_channel(self, session: aiohttp.ClientSession, url: str, headers: dict) -> bool:
        """Test a single channel URL."""
        try:
            async with session.head(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                return 200 <= resp.status < 300
        except Exception:
            return False
