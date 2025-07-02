#!/usr/bin/env python3
"""
Infisical Performance Optimization Engine
Architecture: Memory-C* Infisical Integration Architecture v1.0
Pattern: Performance Optimization with Caching and Connection Management
"""

import os
import json
import time
import logging
import threading
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import pickle
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    access_count: int = 0

    def is_expired(self) -> bool:
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)

@dataclass
class PerformanceMetrics:
    """Performance optimization metrics"""
    cache_hit_rate: float
    avg_secret_load_time: float
    total_requests: int
    cached_requests: int
    optimization_score: float
    memory_usage_mb: float

class InfisicalSecretCache:
    """High-performance secret caching system"""

    def __init__(self, cache_dir: str = "cache/secrets", max_entries: int = 1000):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = max_entries
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0,
            'load_times': []
        }

    def _generate_cache_key(self, env: str, secret_name: Optional[str] = None) -> str:
        """Generate cache key for environment and optional secret"""
        key_data = f"{env}:{secret_name or 'all'}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.cache"

    def _save_to_disk_cache(self, cache_key: str, entry: CacheEntry):
        """Save cache entry to disk"""
        try:
            cache_file = self._get_cache_file_path(cache_key)
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
        except Exception as e:
            logger.warning(f"Failed to save cache to disk: {e}")

    def _load_from_disk_cache(self, cache_key: str) -> Optional[CacheEntry]:
        """Load cache entry from disk"""
        try:
            cache_file = self._get_cache_file_path(cache_key)
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache from disk: {e}")
        return None

    def get_cached_secrets(self, env: str, secret_name: Optional[str] = None) -> Optional[Dict]:
        """Get cached secrets with performance tracking"""
        cache_key = self._generate_cache_key(env, secret_name)

        with self.cache_lock:
            self.metrics['total_requests'] += 1

            # Check memory cache first
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                if not entry.is_expired():
                    entry.access_count += 1
                    self.metrics['hits'] += 1
                    logger.debug(f"Memory cache hit for {env}:{secret_name}")
                    return entry.data
                else:
                    # Remove expired entry
                    del self.memory_cache[cache_key]

            # Check disk cache
            disk_entry = self._load_from_disk_cache(cache_key)
            if disk_entry and not disk_entry.is_expired():
                # Restore to memory cache
                self.memory_cache[cache_key] = disk_entry
                disk_entry.access_count += 1
                self.metrics['hits'] += 1
                logger.debug(f"Disk cache hit for {env}:{secret_name}")
                return disk_entry.data

            # Cache miss
            self.metrics['misses'] += 1
            return None

    def cache_secrets(self, env: str, secrets_data: Dict, ttl_seconds: int = 300, secret_name: Optional[str] = None):
        """Cache secrets with TTL"""
        cache_key = self._generate_cache_key(env, secret_name)

        entry = CacheEntry(
            data=secrets_data,
            timestamp=datetime.now(),
            ttl_seconds=ttl_seconds,
            access_count=1
        )

        with self.cache_lock:
            # Memory cache management
            if len(self.memory_cache) >= self.max_entries:
                # Remove least recently used entry
                lru_key = min(self.memory_cache.keys(),
                             key=lambda k: self.memory_cache[k].access_count)
                del self.memory_cache[lru_key]

            self.memory_cache[cache_key] = entry

            # Save to disk cache for persistence
            self._save_to_disk_cache(cache_key, entry)

        logger.debug(f"Cached secrets for {env}:{secret_name}")

    def invalidate_cache(self, env: Optional[str] = None):
        """Invalidate cache for environment or all"""
        with self.cache_lock:
            if env:
                # Invalidate specific environment
                keys_to_remove = [k for k in self.memory_cache.keys()
                                if k.startswith(self._generate_cache_key(env)[:8])]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                    cache_file = self._get_cache_file_path(key)
                    if cache_file.exists():
                        cache_file.unlink()
            else:
                # Clear all cache
                self.memory_cache.clear()
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()

        logger.info(f"Cache invalidated for {env or 'all environments'}")

    def get_cache_statistics(self) -> Dict:
        """Get cache performance statistics"""
        with self.cache_lock:
            total_requests = self.metrics['total_requests']
            hit_rate = (self.metrics['hits'] / total_requests) if total_requests > 0 else 0

            return {
                'hit_rate': hit_rate,
                'total_requests': total_requests,
                'cache_hits': self.metrics['hits'],
                'cache_misses': self.metrics['misses'],
                'memory_entries': len(self.memory_cache),
                'avg_load_time': sum(self.metrics['load_times']) / len(self.metrics['load_times']) if self.metrics['load_times'] else 0
            }

class InfisicalPerformanceOptimizer:
    """Main performance optimization engine"""

    def __init__(self):
        self.cache = InfisicalSecretCache()
        self.connection_pool = self._initialize_connection_pool()
        self.optimization_config = self._load_optimization_config()
        self.metrics_history: List[PerformanceMetrics] = []

    def _initialize_connection_pool(self) -> Dict:
        """Initialize connection pooling configuration"""
        return {
            'max_concurrent_requests': 5,
            'request_timeout': 10,
            'retry_count': 3,
            'backoff_factor': 0.5
        }

    def _load_optimization_config(self) -> Dict:
        """Load optimization configuration"""
        config_file = Path("configs/infisical-optimization.json")

        default_config = {
            'cache_ttl_seconds': 300,
            'enable_prefetching': True,
            'prefetch_environments': ['dev', 'staging'],
            'batch_size': 10,
            'performance_thresholds': {
                'max_load_time_seconds': 2.0,
                'min_cache_hit_rate': 0.8,
                'max_memory_usage_mb': 100
            }
        }

        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")

        # Save default config
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def get_secrets_optimized(self, env: str, secret_name: Optional[str] = None, force_refresh: bool = False) -> Dict:
        """Get secrets with optimization"""
        start_time = time.time()

        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = self.cache.get_cached_secrets(env, secret_name)
            if cached_data:
                load_time = time.time() - start_time
                self.cache.metrics['load_times'].append(load_time)
                logger.debug(f"Served {env}:{secret_name} from cache in {load_time:.3f}s")
                return cached_data

        # Fetch from Infisical with optimizations
        try:
            secrets_data = self._fetch_secrets_with_retry(env, secret_name)
            load_time = time.time() - start_time

            # Cache the results
            self.cache.cache_secrets(
                env,
                secrets_data,
                ttl_seconds=self.optimization_config['cache_ttl_seconds'],
                secret_name=secret_name
            )

            self.cache.metrics['load_times'].append(load_time)
            logger.info(f"Fetched {env}:{secret_name} in {load_time:.3f}s")

            return secrets_data

        except Exception as e:
            logger.error(f"Failed to fetch secrets for {env}: {e}")
            # Try to return stale cache data as fallback
            cached_data = self.cache.get_cached_secrets(env, secret_name)
            if cached_data:
                logger.warning(f"Returning stale cache data for {env} due to fetch failure")
                return cached_data
            raise

    def _fetch_secrets_with_retry(self, env: str, secret_name: Optional[str] = None) -> Dict:
        """Fetch secrets with retry logic and connection pooling"""
        pool_config = self.connection_pool

        for attempt in range(pool_config['retry_count']):
            try:
                # Build Infisical command
                cmd = ['infisical', 'secrets', '--env', env, '--format', 'json']
                if secret_name:
                    cmd.extend(['--secret-name', secret_name])

                # Execute with timeout
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=pool_config['request_timeout']
                )

                if result.returncode == 0:
                    # Parse JSON response
                    secrets_data = json.loads(result.stdout)
                    return secrets_data
                else:
                    raise Exception(f"Infisical CLI error: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < pool_config['retry_count'] - 1:
                    time.sleep(pool_config['backoff_factor'] * (2 ** attempt))
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < pool_config['retry_count'] - 1:
                    time.sleep(pool_config['backoff_factor'] * (2 ** attempt))
                else:
                    raise

        raise Exception(f"Failed to fetch secrets after {pool_config['retry_count']} attempts")

    def prefetch_secrets(self, environments: Optional[List[str]] = None):
        """Prefetch secrets for common environments"""
        if not self.optimization_config['enable_prefetching']:
            return

        environments = environments or self.optimization_config['prefetch_environments']

        logger.info(f"🚀 Prefetching secrets for environments: {environments}")

        for env in environments:
            try:
                logger.info(f"Prefetching secrets for {env}...")
                self.get_secrets_optimized(env, force_refresh=True)
            except Exception as e:
                logger.warning(f"Failed to prefetch {env}: {e}")

    def optimize_cache_settings(self) -> Dict:
        """Analyze and optimize cache settings"""
        cache_stats = self.cache.get_cache_statistics()

        recommendations = []
        new_config = self.optimization_config.copy()

        # Analyze cache hit rate
        if cache_stats['hit_rate'] < 0.5:
            recommendations.append("Increase cache TTL to improve hit rate")
            new_config['cache_ttl_seconds'] = min(900, new_config['cache_ttl_seconds'] * 1.5)
        elif cache_stats['hit_rate'] > 0.95:
            recommendations.append("Consider reducing cache TTL to ensure fresher data")
            new_config['cache_ttl_seconds'] = max(60, new_config['cache_ttl_seconds'] * 0.8)

        # Analyze load times
        if cache_stats['avg_load_time'] > 2.0:
            recommendations.append("Enable more aggressive prefetching")
            new_config['enable_prefetching'] = True
            if len(new_config['prefetch_environments']) < 3:
                new_config['prefetch_environments'].append('prod')

        # Update configuration if changes recommended
        if recommendations:
            config_file = Path("configs/infisical-optimization.json")
            with open(config_file, 'w') as f:
                json.dump(new_config, f, indent=2)
            self.optimization_config = new_config

            logger.info("✅ Cache optimization completed")
            for rec in recommendations:
                logger.info(f"  📝 {rec}")

        return {
            'recommendations': recommendations,
            'new_config': new_config,
            'current_stats': cache_stats
        }

    def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive performance metrics"""
        cache_stats = self.cache.get_cache_statistics()

        # Calculate memory usage (simplified)
        memory_usage_mb = len(self.cache.memory_cache) * 0.1  # Rough estimate

        # Calculate optimization score (0-100)
        hit_rate_score = cache_stats['hit_rate'] * 40  # 40% weight
        load_time_score = max(0, 40 - (cache_stats['avg_load_time'] * 20))  # 40% weight
        memory_score = max(0, 20 - (memory_usage_mb / 5))  # 20% weight

        optimization_score = hit_rate_score + load_time_score + memory_score

        metrics = PerformanceMetrics(
            cache_hit_rate=cache_stats['hit_rate'],
            avg_secret_load_time=cache_stats['avg_load_time'],
            total_requests=cache_stats['total_requests'],
            cached_requests=cache_stats['cache_hits'],
            optimization_score=optimization_score,
            memory_usage_mb=memory_usage_mb
        )

        self.metrics_history.append(metrics)
        return metrics

    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        current_metrics = self.collect_performance_metrics()
        cache_stats = self.cache.get_cache_statistics()

        # Performance grade
        score = current_metrics.optimization_score
        if score >= 90:
            grade = "A+"
        elif score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"

        # Trend analysis
        trends = {}
        if len(self.metrics_history) >= 2:
            prev_metrics = self.metrics_history[-2]
            trends = {
                'hit_rate_trend': current_metrics.cache_hit_rate - prev_metrics.cache_hit_rate,
                'load_time_trend': current_metrics.avg_secret_load_time - prev_metrics.avg_secret_load_time,
                'optimization_trend': current_metrics.optimization_score - prev_metrics.optimization_score
            }

        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_grade': grade,
            'optimization_score': score,
            'current_metrics': asdict(current_metrics),
            'cache_statistics': cache_stats,
            'trends': trends,
            'configuration': self.optimization_config,
            'recommendations': self._generate_recommendations(current_metrics)
        }

        # Save report
        report_file = Path("reports/infisical-performance-report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def _generate_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        if metrics.cache_hit_rate < 0.7:
            recommendations.append("🔄 Consider increasing cache TTL or enabling prefetching")

        if metrics.avg_secret_load_time > 2.0:
            recommendations.append("⚡ Implement connection pooling or reduce request timeout")

        if metrics.memory_usage_mb > 50:
            recommendations.append("💾 Consider reducing cache size or implementing LRU eviction")

        if metrics.optimization_score < 70:
            recommendations.append("🎯 Overall performance needs improvement - review configuration")

        if not recommendations:
            recommendations.append("✅ Performance is optimal - no changes needed")

        return recommendations

def main():
    """Main optimization function"""
    print("⚡ Infisical Performance Optimization Engine")
    print("Architecture: Memory-C* Infisical Integration v1.0")
    print("=" * 55)

    optimizer = InfisicalPerformanceOptimizer()

    try:
        # Test basic functionality
        logger.info("🔧 Testing optimization engine...")

        # Prefetch common secrets
        optimizer.prefetch_secrets()

        # Collect initial metrics
        metrics = optimizer.collect_performance_metrics()

        # Optimize cache settings
        optimization_result = optimizer.optimize_cache_settings()

        # Generate performance report
        report = optimizer.generate_performance_report()

        # Display results
        print("\n📊 Performance Report:")
        print(f"  Grade: {report['performance_grade']}")
        print(f"  Score: {report['optimization_score']:.1f}/100")
        print(f"  Cache Hit Rate: {metrics.cache_hit_rate:.1%}")
        print(f"  Avg Load Time: {metrics.avg_secret_load_time:.3f}s")
        print(f"  Memory Usage: {metrics.memory_usage_mb:.1f}MB")

        print("\n🎯 Recommendations:")
        for rec in report['recommendations']:
            print(f"  {rec}")

        if optimization_result['recommendations']:
            print("\n🔧 Optimizations Applied:")
            for opt in optimization_result['recommendations']:
                print(f"  ✅ {opt}")

        print("\n📋 Report saved to: reports/infisical-performance-report.json")

        # Store success in memory system
        if os.system("command -v ai-add-smart >/dev/null 2>&1") == 0:
            os.system(f'ai-add-smart "SUCCESS: Infisical performance optimization completed - Grade: {report["performance_grade"]}, Score: {report["optimization_score"]:.1f}/100"')

        return 0

    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())