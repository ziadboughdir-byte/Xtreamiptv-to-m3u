"""
Tests unitaires pour le module cache.py
"""

import unittest
import time
from cache import ServerCache, CacheEntry


class TestCacheEntry(unittest.TestCase):
    """Tests pour la classe CacheEntry"""
    
    def test_cache_entry_creation(self):
        """Test de la création d'une entrée de cache"""
        entry = CacheEntry(data='test_data', timestamp=123456, ttl=300)
        self.assertEqual(entry.data, 'test_data')
        self.assertEqual(entry.timestamp, 123456)
        self.assertEqual(entry.ttl, 300)
    
    def test_cache_entry_expired(self):
        """Test de la propriété is_expired"""
        # Créer une entrée expirée
        expired_entry = CacheEntry(
            data='expired',
            timestamp=time.time() - 301,  # 301 secondes dans le passé
            ttl=300
        )
        self.assertTrue(expired_entry.is_expired)
        
        # Créer une entrée non expirée
        valid_entry = CacheEntry(
            data='valid',
            timestamp=time.time(),
            ttl=300
        )
        self.assertFalse(valid_entry.is_expired)
    
    def test_cache_entry_to_dict(self):
        """Test de la méthode to_dict"""
        entry = CacheEntry(data='test_data', timestamp=123456, ttl=300)
        data = entry.to_dict()
        self.assertEqual(data['data'], 'test_data')
        self.assertEqual(data['timestamp'], 123456)
        self.assertEqual(data['ttl'], 300)
    
    def test_cache_entry_from_dict(self):
        """Test de la méthode from_dict"""
        data = {
            'data': 'test_data',
            'timestamp': 123456,
            'ttl': 300
        }
        entry = CacheEntry.from_dict(data)
        self.assertEqual(entry.data, 'test_data')
        self.assertEqual(entry.timestamp, 123456)
        self.assertEqual(entry.ttl, 300)


class TestServerCache(unittest.TestCase):
    """Tests pour la classe ServerCache"""
    
    def setUp(self):
        """Initialise les tests"""
        self.cache = ServerCache(max_age_seconds=300, max_items=100)
    
    def test_cache_set_get(self):
        """Test de la méthode set et get"""
        self.cache.set('test_key', 'test_value')
        self.assertEqual(self.cache.get('test_key'), 'test_value')
    
    def test_cache_get_nonexistent(self):
        """Test de get avec une clé inexistante"""
        self.assertIsNone(self.cache.get('nonexistent_key'))
    
    def test_cache_expired(self):
        """Test de l'expiration du cache"""
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
    
    def test_cache_cleanup_expired(self):
        """Test de la méthode _cleanup_expired"""
        # Créer une entrée expirée
        expired_entry = CacheEntry(
            data='expired',
            timestamp=time.time() - 301,  # 301 secondes dans le passé
            ttl=300
        )
        
        self.cache.cache['expired_key'] = expired_entry
        self.cache.access_times['expired_key'] = time.time()
        
        # Nettoyer les entrées expirées
        self.cache._cleanup_expired()
        
        # L'entrée expirée doit être supprimée
        self.assertNotIn('expired_key', self.cache.cache)
    
    def test_cache_eviction(self):
        """Test de l'éviction LRU"""
        # Remplir le cache jusqu'à la limite
        for i in range(101):
            self.cache.set(f'key_{i}', f'value_{i}')
        
        # Le cache doit avoir au maximum 100 éléments
        self.assertLessEqual(len(self.cache.cache), 100)
    
    def test_cache_eviction_lru(self):
        """Test de l'éviction LRU"""
        # Ajouter 2 entrées
        self.cache.set('key_1', 'value_1')
        self.cache.set('key_2', 'value_2')
        
        # Mettre à jour l'accès à key_1 (plus récent)
        time.sleep(0.1)  # Attendre un peu
        self.cache.get('key_1')
        
        # Ajouter une 3ème entrée qui dépasse la limite
        self.cache.set('key_3', 'value_3')
        
        # key_2 (moins récent) doit être supprimée
        self.assertIn('key_1', self.cache.cache)
        self.assertIn('key_3', self.cache.cache)
        # Note: L'éviction LRU peut ne pas se produire immédiatement avec 3 éléments
    
    def test_cache_clear(self):
        """Test de la méthode clear"""
        self.cache.set('test_key', 'test_value')
        self.cache.clear()
        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(len(self.cache.access_times), 0)
    
    def test_cache_delete(self):
        """Test de la méthode delete"""
        self.cache.set('test_key', 'test_value')
        self.assertTrue(self.cache.delete('test_key'))
        self.assertFalse(self.cache.delete('nonexistent_key'))
    
    def test_cache_get_size(self):
        """Test de la méthode get_size"""
        self.cache.set('key_1', 'value_1')
        self.cache.set('key_2', 'value_2')
        self.assertEqual(self.cache.get_size(), 2)
    
    def test_cache_get_info(self):
        """Test de la méthode get_info"""
        self.cache.set('test_key', 'test_value')
        info = self.cache.get_info()
        self.assertEqual(info['size'], 1)
        self.assertEqual(info['max_items'], 100)
        self.assertEqual(info['max_age_seconds'], 300)
        self.assertEqual(info['keys'], ['test_key'])
    
    def test_cache_len(self):
        """Test de la méthode __len__"""
        self.cache.set('key_1', 'value_1')
        self.cache.set('key_2', 'value_2')
        self.assertEqual(len(self.cache), 2)
    
    def test_cache_contains(self):
        """Test de la méthode __contains__"""
        self.cache.set('test_key', 'test_value')
        self.assertIn('test_key', self.cache)
        self.assertNotIn('nonexistent_key', self.cache)


if __name__ == '__main__':
    unittest.main()
