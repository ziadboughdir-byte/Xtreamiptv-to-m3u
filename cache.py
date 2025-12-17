"""
Module de cache pour l'application IPTV to M3U Converter
Gère le cache des informations serveur pour améliorer les performances
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class CacheEntry:
    """Représente une entrée dans le cache"""
    data: Any
    timestamp: float
    ttl: float  # Time to live en secondes
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée"""
        return time.time() > self.timestamp + self.ttl
    
    def to_dict(self) -> Dict:
        """Convertit l'entrée en dictionnaire"""
        return {
            'data': self.data,
            'timestamp': self.timestamp,
            'ttl': self.ttl
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        """Crée une entrée à partir d'un dictionnaire"""
        return cls(
            data=data['data'],
            timestamp=data['timestamp'],
            ttl=data['ttl']
        )

class ServerCache:
    """
    Gestionnaire de cache pour les informations serveur
    """
    
    def __init__(self, max_age_seconds: int = 300, max_items: int = 100):
        """
        Initialise le cache
        
        Args:
            max_age_seconds: Durée de vie maximale d'une entrée en secondes (par défaut: 300s = 5min)
            max_items: Nombre maximum d'entrées dans le cache (par défaut: 100)
        """
        self.max_age = max_age_seconds
        self.max_items = max_items
        self.cache: Dict[str, CacheEntry] = {}
        self.access_times: Dict[str, float] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une entrée du cache
        
        Args:
            key: Clé de l'entrée à récupérer
            
        Returns:
            Les données si trouvées et non expirées, sinon None
        """
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        
        # Vérifier si l'entrée est expirée
        if entry.is_expired:
            self._remove(key)
            return None
        
        # Mettre à jour le temps d'accès pour LRU
        self.access_times[key] = time.time()
        
        return entry.data
    
    def set(self, key: str, value: Any) -> None:
        """
        Ajoute ou met à jour une entrée dans le cache
        
        Args:
            key: Clé de l'entrée
            value: Données à stocker
        """
        # Nettoyer les entrées expirées avant d'ajouter
        self._cleanup_expired()
        
        # Vérifier si on dépasse la limite d'items
        if len(self.cache) >= self.max_items:
            self._evict_lru()
        
        # Ajouter ou mettre à jour l'entrée
        self.cache[key] = CacheEntry(
            data=value,
            timestamp=time.time(),
            ttl=self.max_age
        )
        self.access_times[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache
        
        Args:
            key: Clé de l'entrée à supprimer
            
        Returns:
            True si l'entrée a été supprimée, False sinon
        """
        return self._remove(key)
    
    def clear(self) -> None:
        """Vide complètement le cache"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_size(self) -> int:
        """Retourne le nombre d'entrées dans le cache"""
        return len(self.cache)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Retourne des informations sur le cache
        
        Returns:
            Dictionnaire avec les informations du cache
        """
        return {
            'size': len(self.cache),
            'max_items': self.max_items,
            'max_age_seconds': self.max_age,
            'keys': list(self.cache.keys())
        }
    
    def _remove(self, key: str) -> bool:
        """Supprime une entrée du cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return True
        return False
    
    def _cleanup_expired(self) -> None:
        """Nettoie les entrées expirées"""
        expired_keys = [k for k, v in self.cache.items() if v.is_expired]
        for key in expired_keys:
            self._remove(key)
    
    def _evict_lru(self) -> None:
        """Supprime l'entrée la moins récemment utilisée"""
        if not self.access_times:
            return
        
        # Trouver la clé avec le temps d'accès le plus ancien
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove(lru_key)
    
    def __len__(self) -> int:
        """Retourne le nombre d'entrées dans le cache"""
        return len(self.cache)
    
    def __contains__(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache"""
        return key in self.cache and not self.cache[key].is_expired
