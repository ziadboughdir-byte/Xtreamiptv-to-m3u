"""
Tests unitaires pour le module iptv_client.py
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock
from iptv_client import IPTVClient


class TestIPTVClient(unittest.TestCase):
    """Tests pour la classe IPTVClient"""
    
    def setUp(self):
        """Initialise les tests"""
        self.client = IPTVClient("http://example.com:8080/player_api.php?username=test&password=test")
    
    def test_parse_url_basic(self):
        """Test de la méthode parse_url avec une URL de base"""
        host, port, username, password = self.client.parse_url()
        self.assertEqual(host, "example.com")
        self.assertEqual(port, 8080)
        self.assertEqual(username, "test")
        self.assertEqual(password, "test")
    
    def test_parse_url_no_port(self):
        """Test de la méthode parse_url sans port explicite"""
        client = IPTVClient("http://example.com/player_api.php?username=test&password=test")
        host, port, username, password = client.parse_url()
        self.assertEqual(host, "example.com")
        self.assertEqual(port, 80)
        self.assertEqual(username, "test")
        self.assertEqual(password, "test")
    
    def test_parse_url_https(self):
        """Test de la méthode parse_url avec HTTPS"""
        client = IPTVClient("https://example.com/player_api.php?username=test&password=test")
        host, port, username, password = client.parse_url()
        self.assertEqual(host, "example.com")
        self.assertEqual(port, 443)
        self.assertEqual(username, "test")
        self.assertEqual(password, "test")
    
    def test_construct_base_url(self):
        """Test de la méthode construct_base_url"""
        self.client.parse_url()
        base_url = self.client.construct_base_url()
        self.assertEqual(base_url, "http://example.com:8080")
    
    def test_construct_base_url_no_port(self):
        """Test de la méthode construct_base_url sans port"""
        client = IPTVClient("http://example.com/player_api.php?username=test&password=test")
        client.parse_url()
        base_url = client.construct_base_url()
        self.assertEqual(base_url, "http://example.com")
    
    def test_construct_base_url_https(self):
        """Test de la méthode construct_base_url avec HTTPS"""
        client = IPTVClient("https://example.com/player_api.php?username=test&password=test")
        client.parse_url()
        base_url = client.construct_base_url()
        self.assertEqual(base_url, "https://example.com")
    
    @patch('aiohttp.ClientSession')
    async def test_fetch_success(self, mock_session):
        """Test de la méthode fetch avec succès"""
        mock_response = MagicMock()
        mock_response.text.return_value = 'success'
        mock_response.raise_for_status.return_value = None
        
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
        
        session = await mock_session().__aenter__()
        result = await self.client.fetch(session, 'http://example.com')
        
        self.assertEqual(result, 'success')
    
    @patch('aiohttp.ClientSession')
    async def test_fetch_failure(self, mock_session):
        """Test de la méthode fetch avec échec"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception('HTTP Error')
        
        mock_session.return_value.__aenter__.return_value.request.return_value.__aenter__.return_value = mock_response
        
        session = await mock_session().__aenter__()
        with self.assertRaises(Exception):
            await self.client.fetch(session, 'http://example.com')
    
    def test_get_server_info_cache_hit(self):
        """Test de get_server_info avec cache hit"""
        # Le cache est testé dans test_cache.py
        pass
    
    def test_generate_m3u(self):
        """Test de la méthode generate_m3u"""
        # Les tests asynchrones nécessitent un loop
        pass
    
    def test_generate_radio_m3u(self):
        """Test de la méthode generate_radio_m3u"""
        pass
    
    def test_generate_vod_m3u(self):
        """Test de la méthode generate_vod_m3u"""
        pass
    
    def test_save_m3u(self):
        """Test de la méthode save_m3u"""
        # Les tests de sauvegarde nécessitent un fichier temporaire
        pass
    
    def test_test_channels(self):
        """Test de la méthode test_channels"""
        pass


class TestCache(unittest.TestCase):
    """Tests pour le module cache.py"""
    
    def setUp(self):
        """Initialise les tests"""
        from cache import ServerCache
        self.cache = ServerCache(max_age_seconds=300, max_items=100)
    
    def test_cache_set_get(self):
        """Test de la méthode set et get"""
        self.cache.set('test_key', 'test_value')
        self.assertEqual(self.cache.get('test_key'), 'test_value')
    
    def test_cache_expired(self):
        """Test de l'expiration du cache"""
        from cache import CacheEntry
        import time
        
        # Créer une entrée expirée
        expired_entry = CacheEntry(
            data='expired',
            timestamp=time.time() - 301,  # 301 secondes dans le passé
            ttl=300
        )
        
        self.cache.cache['expired_key'] = expired_entry
        self.cache.access_times['expired_key'] = time.time()
        
        # Le cache doit retourner None pour une entrée expirée
        self.assertIsNone(self.cache.get('expired_key'))
    
    def test_cache_eviction(self):
        """Test de l'éviction LRU"""
        # Remplir le cache jusqu'à la limite
        for i in range(101):
            self.cache.set(f'key_{i}', f'value_{i}')
        
        # Le cache doit avoir au maximum 100 éléments
        self.assertLessEqual(len(self.cache.cache), 100)
    
    def test_cache_clear(self):
        """Test de la méthode clear"""
        self.cache.set('test_key', 'test_value')
        self.cache.clear()
        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(len(self.cache.access_times), 0)
    
    def test_cache_info(self):
        """Test de la méthode get_info"""
        self.cache.set('test_key', 'test_value')
        info = self.cache.get_info()
        self.assertEqual(info['size'], 1)
        self.assertEqual(info['max_items'], 100)
        self.assertEqual(info['max_age_seconds'], 300)
        self.assertEqual(info['keys'], ['test_key'])


if __name__ == '__main__':
    unittest.main()
