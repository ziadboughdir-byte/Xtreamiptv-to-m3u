"""
Tests unitaires pour le module config_manager.py
"""

import unittest
import os
import tempfile
from pathlib import Path
from config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Tests pour la classe ConfigManager"""
    
    def setUp(self):
        """Initialise les tests"""
        # Créer un fichier de configuration temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / 'test_config.ini'
        
        # Créer une instance de ConfigManager
        self.config = ConfigManager(str(self.config_file))
    
    def tearDown(self):
        """Nettoie après les tests"""
        # Supprimer le fichier de configuration temporaire
        if self.config_file.exists():
            self.config_file.unlink()
        
        # Supprimer le répertoire temporaire
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_creation(self):
        """Test de la création du fichier de configuration"""
        self.assertTrue(self.config_file.exists())
    
    def test_config_load(self):
        """Test de la méthode load"""
        self.config.load()
        self.assertIn('app', self.config.config)
        self.assertIn('cache', self.config.config)
        self.assertIn('testing', self.config.config)
        self.assertIn('ui', self.config.config)
        self.assertIn('security', self.config.config)
    
    def test_config_save(self):
        """Test de la méthode save"""
        # Modifier une valeur
        self.config.set('cache', 'max_age_seconds', '600')
        
        # Recharger le fichier
        self.config.load()
        
        # Vérifier que la valeur a été sauvegardée
        self.assertEqual(self.config.get('cache', 'max_age_seconds', 0), 600)
    
    def test_config_get(self):
        """Test de la méthode get"""
        self.assertEqual(self.config.get('app', 'version'), '1.1.0')
        self.assertEqual(self.config.get('cache', 'enabled', False), True)
        self.assertEqual(self.config.get('cache', 'max_age_seconds', 0), 300)
        self.assertEqual(self.config.get('testing', 'max_concurrent_tests', 0), 10)
        self.assertEqual(self.config.get('ui', 'theme'), 'dark')
        self.assertEqual(self.config.get('ui', 'show_password', False), False)
    
    def test_config_get_default(self):
        """Test de la méthode get avec valeur par défaut"""
        self.assertEqual(self.config.get('nonexistent', 'key', 'default'), 'default')
        self.assertEqual(self.config.get('app', 'nonexistent', 'default'), 'default')
    
    def test_config_set(self):
        """Test de la méthode set"""
        self.config.set('cache', 'max_age_seconds', '600')
        self.assertEqual(self.config.get('cache', 'max_age_seconds', 0), 600)
    
    def test_config_set_type_conversion(self):
        """Test de la conversion automatique des types"""
        self.config.set('cache', 'max_age_seconds', 600)
        self.assertEqual(self.config.get('cache', 'max_age_seconds', 0), 600)
        
        self.config.set('cache', 'enabled', False)
        self.assertEqual(self.config.get('cache', 'enabled', False), False)
    
    def test_config_get_section(self):
        """Test de la méthode get_section"""
        cache_section = self.config.get_section('cache')
        self.assertIn('enabled', cache_section)
        self.assertIn('max_age_seconds', cache_section)
        self.assertIn('max_items', cache_section)
        self.assertEqual(cache_section['enabled'], True)
        self.assertEqual(cache_section['max_age_seconds'], 300)
        self.assertEqual(cache_section['max_items'], 100)
    
    def test_config_get_all(self):
        """Test de la méthode get_all"""
        all_config = self.config.get_all()
        self.assertIn('app', all_config)
        self.assertIn('cache', all_config)
        self.assertIn('testing', all_config)
        self.assertIn('ui', all_config)
        self.assertIn('security', all_config)
    
    def test_config_reset_to_defaults(self):
        """Test de la méthode reset_to_defaults"""
        # Modifier une valeur
        self.config.set('cache', 'max_age_seconds', '600')
        
        # Réinitialiser aux valeurs par défaut
        self.config.reset_to_defaults()
        
        # Vérifier que la valeur a été réinitialisée
        self.assertEqual(self.config.get('cache', 'max_age_seconds', 0), 300)
    
    def test_config_delete(self):
        """Test de la méthode delete"""
        # Supprimer une valeur
        self.config.delete('cache', 'max_age_seconds')
        
        # Vérifier que la valeur a été supprimée
        self.assertIsNone(self.config.get('cache', 'max_age_seconds', None))
    
    def test_config_delete_section(self):
        """Test de la méthode delete_section"""
        # Supprimer une section
        self.config.delete_section('cache')
        
        # Vérifier que la section a été supprimée
        self.assertNotIn('cache', self.config.config)
    
    def test_config_cache_config(self):
        """Test de la méthode get_cache_config"""
        cache_config = self.config.get_cache_config()
        self.assertIn('enabled', cache_config)
        self.assertIn('max_age_seconds', cache_config)
        self.assertIn('max_items', cache_config)
    
    def test_config_testing_config(self):
        """Test de la méthode get_testing_config"""
        testing_config = self.config.get_testing_config()
        self.assertIn('max_concurrent_tests', testing_config)
        self.assertIn('timeout_seconds', testing_config)
    
    def test_config_ui_config(self):
        """Test de la méthode get_ui_config"""
        ui_config = self.config.get_ui_config()
        self.assertIn('theme', ui_config)
        self.assertIn('font_size', ui_config)
        self.assertIn('show_password', ui_config)
        self.assertIn('window_width', ui_config)
        self.assertIn('window_height', ui_config)
    
    def test_config_security_config(self):
        """Test de la méthode get_security_config"""
        security_config = self.config.get_security_config()
        self.assertIn('encrypt_passwords', security_config)
        self.assertIn('password_mask', security_config)


if __name__ == '__main__':
    unittest.main()
