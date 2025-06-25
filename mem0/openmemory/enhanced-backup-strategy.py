#!/usr/bin/env python3
"""
Enhanced Backup Strategy for Advanced Memory System
Based on TechTarget's backup testing guidelines and validation results
"""

import json
import subprocess
import shutil
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import logging
import sqlite3
import tarfile

class EnhancedBackupStrategy:
    """Enhanced backup strategy with improved reliability and testing"""
    
    def __init__(self, config_file: str = "enhanced_backup_config.json"):
        self.config = self._load_config(config_file)
        self.backup_root = Path("enhanced_backups")
        self.temp_dir = Path("backup_temp")
        
        self.setup_logging()
        self.ensure_directories()
        self.init_tracking_db()
        
    def setup_logging(self):
        """Setup logging for backup operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('enhanced_backup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load enhanced backup configuration"""
        default_config = {
            "backup_retention_days": 30,
            "backup_schedule": {
                "full_backup": "daily",
                "incremental_backup": "hourly",
                "configuration_backup": "daily"
            },
            "backup_types": {
                "memory_data": {
                    "enabled": True,
                    "method": "sqlite_dump",
                    "compression": True
                },
                "docker_volumes": {
                    "enabled": True,
                    "method": "volume_export",
                    "compression": True
                },
                "application_config": {
                    "enabled": True,
                    "method": "file_copy",
                    "compression": False
                },
                "system_state": {
                    "enabled": True,
                    "method": "metadata_capture",
                    "compression": False
                }
            },
            "redundancy": {
                "local_copies": 2,
                "verify_after_backup": True,
                "test_restoration_frequency": "weekly"
            },
            "validation": {
                "checksum_verification": True,
                "integrity_testing": True,
                "restoration_testing": True
            }
        }
        
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
                
        return default_config
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        self.backup_root.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create structured backup directories
        for backup_type in self.config["backup_types"]:
            (self.backup_root / backup_type).mkdir(exist_ok=True)
    
    def init_tracking_db(self):
        """Initialize backup tracking database"""
        db_path = self.backup_root / "backup_tracking.db"
        
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    file_count INTEGER,
                    size_mb REAL,
                    checksum TEXT,
                    backup_duration_seconds REAL,
                    validation_status TEXT,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS restoration_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    backup_id INTEGER,
                    test_status TEXT NOT NULL,
                    restoration_time_seconds REAL,
                    validation_errors TEXT,
                    FOREIGN KEY (backup_id) REFERENCES backup_records (id)
                )
            """)
    
    def create_memory_data_backup(self) -> Dict[str, Any]:
        """Create comprehensive memory data backup"""
        self.logger.info("💾 Creating memory data backup...")
        
        backup_start = time.time()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_root / "memory_data" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_result = {
            "type": "memory_data",
            "timestamp": timestamp,
            "success": False,
            "files_created": [],
            "total_size_mb": 0,
            "checksum": "",
            "errors": []
        }
        
        try:
            # 1. Export memory analytics
            analytics_file = backup_dir / "memory_analytics.json"
            analytics_result = subprocess.run([
                'python3', '../advanced-memory-ai.py', 'analytics'
            ], capture_output=True, text=True, cwd=backup_dir)
            
            if analytics_result.returncode == 0:
                with open(analytics_file, 'w') as f:
                    f.write(analytics_result.stdout)
                backup_result["files_created"].append(str(analytics_file))
            
            # 2. Export individual memories (sample)
            memories_dir = backup_dir / "memories"
            memories_dir.mkdir(exist_ok=True)
            
            # Create a comprehensive memory export
            memory_export_result = subprocess.run([
                'python3', '../advanced-memory-ai.py', 'search', 'all', 'general'
            ], capture_output=True, text=True, cwd=backup_dir)
            
            if memory_export_result.returncode == 0:
                memories_file = memories_dir / "memory_export.txt"
                with open(memories_file, 'w') as f:
                    f.write(memory_export_result.stdout)
                backup_result["files_created"].append(str(memories_file))
            
            # 3. Backup configuration files
            config_files = [
                '../monitoring_config.json',
                '../alert_config.json', 
                '../backup_test_config.json',
                '../docker-compose.yml'
            ]
            
            config_dir = backup_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            for config_file in config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    dest_path = config_dir / config_path.name
                    shutil.copy2(config_path, dest_path)
                    backup_result["files_created"].append(str(dest_path))
            
            # 4. Create compressed archive
            archive_path = backup_dir.parent / f"{timestamp}_memory_backup.tar.gz"
            
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(backup_dir, arcname=timestamp)
            
            backup_result["files_created"].append(str(archive_path))
            
            # 5. Calculate checksums and sizes
            total_size = 0
            for file_path in backup_result["files_created"]:
                if Path(file_path).exists():
                    total_size += Path(file_path).stat().st_size
            
            backup_result["total_size_mb"] = total_size / (1024 * 1024)
            backup_result["checksum"] = self._calculate_backup_checksum(backup_dir)
            backup_result["success"] = True
            
            # 6. Immediate validation
            validation_result = self._validate_backup_immediately(archive_path)
            if not validation_result["valid"]:
                backup_result["errors"].extend(validation_result["errors"])
                backup_result["success"] = False
            
        except Exception as e:
            backup_result["errors"].append(str(e))
            self.logger.error(f"Memory data backup failed: {e}")
        
        backup_result["duration_seconds"] = time.time() - backup_start
        self._record_backup(backup_result)
        
        return backup_result
    
    def create_docker_volume_backup(self) -> Dict[str, Any]:
        """Create improved Docker volume backup"""
        self.logger.info("🐳 Creating enhanced Docker volume backup...")
        
        backup_start = time.time()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_root / "docker_volumes" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_result = {
            "type": "docker_volumes",
            "timestamp": timestamp,
            "success": False,
            "files_created": [],
            "total_size_mb": 0,
            "checksum": "",
            "errors": []
        }
        
        try:
            # 1. Get Docker volume information
            volumes_info = subprocess.run([
                'docker', 'volume', 'ls', '--format', 'json'
            ], capture_output=True, text=True)
            
            if volumes_info.returncode == 0:
                volumes_file = backup_dir / "volumes_info.json"
                with open(volumes_file, 'w') as f:
                    f.write(volumes_info.stdout)
                backup_result["files_created"].append(str(volumes_file))
            
            # 2. Export mem0 storage volume with improved method
            volume_name = "openmemory_mem0_storage"
            backup_file = backup_dir / f"{volume_name}_backup.tar.gz"
            
            # Use docker run to create backup with absolute path resolution
            backup_cmd = [
                'docker', 'run', '--rm',
                '-v', f'{volume_name}:/source:ro',
                '-v', f'{str(backup_dir.absolute())}:/backup',
                'alpine',
                'tar', 'czf', f'/backup/{volume_name}_backup.tar.gz', '-C', '/source', '.'
            ]
            
            volume_backup_result = subprocess.run(backup_cmd, capture_output=True, text=True)
            
            if volume_backup_result.returncode == 0 and backup_file.exists():
                backup_result["files_created"].append(str(backup_file))
                
                # 3. Create volume manifest
                manifest = {
                    "volume_name": volume_name,
                    "backup_timestamp": timestamp,
                    "backup_method": "docker_run_tar",
                    "compression": "gzip",
                    "file_size_mb": backup_file.stat().st_size / (1024 * 1024)
                }
                
                manifest_file = backup_dir / "volume_manifest.json"
                with open(manifest_file, 'w') as f:
                    json.dump(manifest, f, indent=2)
                backup_result["files_created"].append(str(manifest_file))
            else:
                backup_result["errors"].append(f"Volume backup failed: {volume_backup_result.stderr}")
            
            # 4. Calculate total size and checksum
            total_size = sum(Path(f).stat().st_size for f in backup_result["files_created"] if Path(f).exists())
            backup_result["total_size_mb"] = total_size / (1024 * 1024)
            backup_result["checksum"] = self._calculate_backup_checksum(backup_dir)
            backup_result["success"] = len(backup_result["errors"]) == 0
            
        except Exception as e:
            backup_result["errors"].append(str(e))
            self.logger.error(f"Docker volume backup failed: {e}")
        
        backup_result["duration_seconds"] = time.time() - backup_start
        self._record_backup(backup_result)
        
        return backup_result
    
    def create_application_config_backup(self) -> Dict[str, Any]:
        """Create application configuration backup"""
        self.logger.info("⚙️ Creating application configuration backup...")
        
        backup_start = time.time()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backup_root / "application_config" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_result = {
            "type": "application_config",
            "timestamp": timestamp,
            "success": False,
            "files_created": [],
            "total_size_mb": 0,
            "checksum": "",
            "errors": []
        }
        
        try:
            # Important configuration files to backup
            config_sources = [
                ('docker-compose.yml', '../docker-compose.yml'),
                ('maintenance_config.json', '../monitoring_config.json'),
                ('alert_config.json', '../alert_config.json'),
                ('cron_maintenance.sh', '../cron-maintenance.sh'),
                ('maintenance_schedule.sh', '../maintenance-schedule.sh'),
                ('week_monitor.py', '../week-monitor.py'),
                ('advanced_memory_ai.py', '../advanced-memory-ai.py')
            ]
            
            for dest_name, source_path in config_sources:
                source_file = Path(source_path)
                if source_file.exists():
                    dest_file = backup_dir / dest_name
                    shutil.copy2(source_file, dest_file)
                    backup_result["files_created"].append(str(dest_file))
            
            # Create application state snapshot
            state_file = backup_dir / "application_state.json"
            app_state = {
                "backup_timestamp": timestamp,
                "python_version": subprocess.run(['python3', '--version'], 
                                               capture_output=True, text=True).stdout.strip(),
                "docker_version": subprocess.run(['docker', '--version'], 
                                               capture_output=True, text=True).stdout.strip(),
                "system_info": {
                    "backup_dir_size": sum(f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()),
                    "file_count": len(list(backup_dir.rglob("*")))
                }
            }
            
            with open(state_file, 'w') as f:
                json.dump(app_state, f, indent=2)
            backup_result["files_created"].append(str(state_file))
            
            # Calculate totals
            total_size = sum(Path(f).stat().st_size for f in backup_result["files_created"])
            backup_result["total_size_mb"] = total_size / (1024 * 1024)
            backup_result["checksum"] = self._calculate_backup_checksum(backup_dir)
            backup_result["success"] = True
            
        except Exception as e:
            backup_result["errors"].append(str(e))
            self.logger.error(f"Application config backup failed: {e}")
        
        backup_result["duration_seconds"] = time.time() - backup_start
        self._record_backup(backup_result)
        
        return backup_result
    
    def _calculate_backup_checksum(self, backup_dir: Path) -> str:
        """Calculate comprehensive checksum for backup directory"""
        hash_obj = hashlib.sha256()
        
        try:
            for file_path in sorted(backup_dir.rglob("*")):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_obj.update(chunk)
                    hash_obj.update(str(file_path.relative_to(backup_dir)).encode())
        except Exception as e:
            self.logger.error(f"Checksum calculation error: {e}")
            return "checksum_error"
        
        return hash_obj.hexdigest()[:16]
    
    def _validate_backup_immediately(self, backup_path: Path) -> Dict[str, Any]:
        """Immediate validation of created backup"""
        validation_result = {
            "valid": True,
            "errors": []
        }
        
        try:
            if backup_path.suffix == '.gz' and backup_path.name.endswith('.tar.gz'):
                # Test tar.gz archive
                with tarfile.open(backup_path, 'r:gz') as tar:
                    members = tar.getmembers()
                    if len(members) == 0:
                        validation_result["valid"] = False
                        validation_result["errors"].append("Archive is empty")
                    
                    # Test extraction of first few files
                    for member in members[:5]:
                        if member.isfile():
                            try:
                                tar.extractfile(member).read(1024)
                            except Exception as e:
                                validation_result["valid"] = False
                                validation_result["errors"].append(f"Cannot extract {member.name}: {e}")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {e}")
        
        return validation_result
    
    def _record_backup(self, backup_result: Dict[str, Any]):
        """Record backup in tracking database"""
        db_path = self.backup_root / "backup_tracking.db"
        
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO backup_records (
                    timestamp, backup_type, backup_path, file_count,
                    size_mb, checksum, backup_duration_seconds,
                    validation_status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                backup_result["type"],
                str(backup_result.get("files_created", [])),
                len(backup_result.get("files_created", [])),
                backup_result["total_size_mb"],
                backup_result["checksum"],
                backup_result["duration_seconds"],
                "PASSED" if backup_result["success"] else "FAILED",
                json.dumps(backup_result.get("errors", []))
            ))
    
    def run_comprehensive_backup(self) -> Dict[str, Any]:
        """Run comprehensive backup of all components"""
        self.logger.info("🚀 Starting comprehensive enhanced backup...")
        
        comprehensive_start = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "backups": [],
            "summary": {
                "total_backups": 0,
                "successful_backups": 0,
                "failed_backups": 0,
                "total_size_mb": 0,
                "total_duration_minutes": 0
            },
            "overall_status": "RUNNING"
        }
        
        try:
            # Run all backup types
            backup_methods = [
                self.create_memory_data_backup,
                self.create_docker_volume_backup,
                self.create_application_config_backup
            ]
            
            for backup_method in backup_methods:
                try:
                    backup_result = backup_method()
                    results["backups"].append(backup_result)
                    
                    if backup_result["success"]:
                        results["summary"]["successful_backups"] += 1
                    else:
                        results["summary"]["failed_backups"] += 1
                    
                    results["summary"]["total_size_mb"] += backup_result["total_size_mb"]
                    
                except Exception as e:
                    self.logger.error(f"Backup method failed: {e}")
                    results["backups"].append({
                        "type": "unknown",
                        "success": False,
                        "errors": [str(e)]
                    })
                    results["summary"]["failed_backups"] += 1
            
            results["summary"]["total_backups"] = len(results["backups"])
            results["summary"]["total_duration_minutes"] = (time.time() - comprehensive_start) / 60
            
            # Determine overall status
            if results["summary"]["failed_backups"] == 0:
                results["overall_status"] = "SUCCESS"
            elif results["summary"]["successful_backups"] > 0:
                results["overall_status"] = "PARTIAL_SUCCESS"
            else:
                results["overall_status"] = "FAILED"
            
        except Exception as e:
            results["overall_status"] = "ERROR"
            results["error"] = str(e)
            self.logger.error(f"Comprehensive backup error: {e}")
        
        # Save results
        self._save_backup_report(results)
        return results
    
    def _save_backup_report(self, results: Dict[str, Any]):
        """Save comprehensive backup report"""
        report_file = self.backup_root / f"backup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"📊 Backup report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save backup report: {e}")

def main():
    """Main enhanced backup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Memory System Backup Strategy")
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive backup')
    parser.add_argument('--memory', action='store_true', help='Backup memory data only')
    parser.add_argument('--docker', action='store_true', help='Backup Docker volumes only')
    parser.add_argument('--config', action='store_true', help='Backup configuration only')
    
    args = parser.parse_args()
    
    backup_strategy = EnhancedBackupStrategy()
    
    if args.comprehensive:
        results = backup_strategy.run_comprehensive_backup()
        print(f"✅ Comprehensive backup completed. Status: {results['overall_status']}")
        print(f"   Successful: {results['summary']['successful_backups']}")
        print(f"   Failed: {results['summary']['failed_backups']}")
        print(f"   Total Size: {results['summary']['total_size_mb']:.2f} MB")
        return
    
    if args.memory:
        result = backup_strategy.create_memory_data_backup()
        print(f"💾 Memory backup: {'SUCCESS' if result['success'] else 'FAILED'}")
        return
    
    if args.docker:
        result = backup_strategy.create_docker_volume_backup()
        print(f"🐳 Docker backup: {'SUCCESS' if result['success'] else 'FAILED'}")
        return
    
    if args.config:
        result = backup_strategy.create_application_config_backup()
        print(f"⚙️ Config backup: {'SUCCESS' if result['success'] else 'FAILED'}")
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main() 