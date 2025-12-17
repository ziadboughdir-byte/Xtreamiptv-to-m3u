"""
Gestionnaire de configuration pour l'application IPTV to M3U Converter
"""

import configparser
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigManager:
    """
    Gestionnaire de configuration pour l'application
    """
    
    def __init__(self, config_file: str = "config.ini"):
        """
        Initialise le gestionnaire de configuration
        
        Args:
            config_file: Chemin vers le fichier de configuration
        """
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self) -> None:
        """Charge la configuration depuis le fichier"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            # Créer un fichier de configuration par défaut
            self._create_default_config()
            self.save()
    
    def save(self) -> None:
        """Sauvegarde la configuration dans le fichier"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def _create_default_config(self) -> None:
        """Crée un fichier de configuration par défaut"""
        self.config['app'] = {
            'version': '1.1.0',
            'name': 'IPTV to M3U Converter',
            'author': 'ZiadBoughdir',
            'last_update': '2025-01-01'
        }
        
        self.config['cache'] = {
            'enabled': 'True',
            'max_age_seconds': '300',
            'max_items': '100'
        }
        
        self.config['testing'] = {
            'max_concurrent_tests': '10',
            'timeout_seconds': '5'
        }
        
        self.config['ui'] = {
            'theme': 'dark',
            'font_size': '12',
            'show_password': 'False',
            'window_width': '1000',
            'window_height': '700'
        }
        
        self.config['security'] = {
            'encrypt_passwords': 'False',
            'password_mask': '••••••••'
        }
    
    def get(self, section: str, key: str, default: Optional[Any] = None) -> Any:
        """
        Récupère une valeur de configuration
        
        Args:
            section: Section du fichier de configuration
            key: Clé de la configuration
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            La valeur de configuration
        """
        try:
            if section not in self.config:
                return default
            
            value = self.config[section].get(key, default)
            
            # Convertir automatiquement les types
            if value is not None:
                if isinstance(default, bool):
                    return self.config[section].getboolean(key, default)
                elif isinstance(default, int):
                    return self.config[section].getint(key, default)
                elif isinstance(default, float):
                    return self.config[section].getfloat(key, default)
            
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Définit une valeur de configuration
        
        Args:
            section: Section du fichier de configuration
            key: Clé de la configuration
            value: Valeur à stocker
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = str(value)
        self.save()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Récupère toutes les valeurs d'une section
        
        Args:
            section: Section du fichier de configuration
            
        Returns:
            Dictionnaire avec toutes les clés/valeurs de la section
        """
        if section not in self.config:
            return {}
        
        result = {}
        for key, value in self.config[section].items():
            # Convertir automatiquement les types
            try:
                if value.lower() in ['true', 'false']:
                    result[key] = self.config[section].getboolean(key)
                elif '.' in value:
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except ValueError:
                result[key] = value
        
        return result
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Récupère toutes les configurations
        
        Returns:
            Dictionnaire imbriqué avec toutes les sections et valeurs
        """
        result = {}
        for section in self.config.sections():
            result[section] = self.get_section(section)
        return result
    
    def reset_to_defaults(self) -> None:
        """Réinitialise la configuration aux valeurs par défaut"""
        self.config.clear()
        self._create_default_config()
        self.save()
    
    def delete(self, section: str, key: str) -> None:
        """
        Supprime une valeur de configuration
        
        Args:
            section: Section du fichier de configuration
            key: Clé de la configuration
        """
        if section in self.config and key in self.config[section]:
            del self.config[section][key]
            self.save()
    
    def delete_section(self, section: str) -> None:
        """
        Supprime une section complète
        
        Args:
            section: Section du fichier de configuration
        """
        if section in self.config:
            del self.config[section]
            self.save()
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Récupère la configuration du cache"""
        return self.get_section('cache')
    
    def get_testing_config(self) -> Dict[str, Any]:
        """Récupère la configuration des tests"""
        return self.get_section('testing')
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Récupère la configuration de l'interface utilisateur"""
        return self.get_section('ui')
    
    def get_security_config(self) -> Dict[str, Any]:
        """Récupère la configuration de sécurité"""
        return self.get_section('security')


# Instance globale du gestionnaire de configuration
CONFIG = ConfigManager()
