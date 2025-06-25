#!/usr/bin/env python3
"""
Advanced Memory System - Backup Validation Framework
Following TechTarget's 10-step guide and MSP360's comprehensive backup testing practices
"""

import asyncio
import json
import subprocess
import time
import hashlib
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import os
import logging
import tarfile
import zipfile

class BackupValidator:
    """Comprehensive backup validation and testing system"""
    
    def __init__(self, config_file: str = "backup_test_config.json"):
        self.config = self._load_config(config_file)
        self.test_db = Path("backup_validation.db")
        self.backup_dir = Path("backups")
        self.test_workspace = Path("backup_test_workspace")
        
        self.setup_logging()
        self.init_database()
        self.ensure_directories()
        
    def setup_logging(self):
        """Setup logging for backup validation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('backup_validation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load backup testing configuration"""
        default_config = {
            "test_schedule": {
                "full_restore_test": "weekly",
                "integrity_check": "daily", 
                "performance_benchmark": "monthly"
            },
            "rto_target_minutes": 30,  # Recovery Time Objective
            "rpo_target_minutes": 15,  # Recovery Point Objective
            "test_data_retention_days": 30,
            "backup_sources": [
                "docker_volumes",
                "configuration_files", 
                "database_files",
                "application_state"
            ],
            "validation_methods": [
                "file_integrity",
                "database_consistency",
                "application_state",
                "configuration_validity"
            ],
            "alert_thresholds": {
                "restore_time_minutes": 45,
                "integrity_failure_rate": 0.01,
                "backup_size_variance": 0.25
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
    
    def init_database(self):
        """Initialize backup validation database"""
        with sqlite3.connect(self.test_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    backup_source TEXT NOT NULL,
                    test_status TEXT NOT NULL,
                    duration_seconds REAL,
                    restore_time_minutes REAL,
                    integrity_score REAL,
                    file_count INTEGER,
                    backup_size_mb REAL,
                    test_notes TEXT,
                    error_details TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    file_count INTEGER,
                    total_size_mb REAL,
                    checksum TEXT,
                    created_date TEXT,
                    verified_date TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recovery_benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    scenario TEXT NOT NULL,
                    recovery_time_minutes REAL,
                    data_loss_minutes REAL,
                    success_rate REAL,
                    performance_notes TEXT
                )
            """)
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        self.backup_dir.mkdir(exist_ok=True)
        self.test_workspace.mkdir(exist_ok=True)
    
    def discover_backups(self) -> List[Dict[str, Any]]:
        """Discover and catalog existing backups"""
        self.logger.info("🔍 Discovering existing backups...")
        
        backups = []
        
        # Discover automated maintenance backups
        for backup_path in self.backup_dir.glob("*/"):
            if backup_path.is_dir():
                backup_info = self._analyze_backup_directory(backup_path)
                if backup_info:
                    backups.append(backup_info)
                    self._register_backup(backup_info)
        
        # Discover Docker volume backups
        docker_backups = self._discover_docker_backups()
        backups.extend(docker_backups)
        
        self.logger.info(f"📦 Discovered {len(backups)} backup sets")
        return backups
    
    def _analyze_backup_directory(self, backup_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a backup directory structure"""
        try:
            files = list(backup_path.rglob("*"))
            file_count = len([f for f in files if f.is_file()])
            
            if file_count == 0:
                return None
            
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            return {
                "path": str(backup_path),
                "type": "directory_backup",
                "file_count": file_count,
                "total_size_mb": total_size / (1024 * 1024),
                "created_date": datetime.fromtimestamp(backup_path.stat().st_ctime).isoformat(),
                "checksum": self._calculate_directory_checksum(backup_path)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing backup {backup_path}: {e}")
            return None
    
    def _discover_docker_backups(self) -> List[Dict[str, Any]]:
        """Discover Docker volume backups"""
        backups = []
        
        try:
            # Look for tar.gz files that might be Docker backups
            for backup_file in self.backup_dir.rglob("*.tar.gz"):
                if "mem0_storage" in backup_file.name:
                    backup_info = {
                        "path": str(backup_file),
                        "type": "docker_volume_backup",
                        "file_count": 1,
                        "total_size_mb": backup_file.stat().st_size / (1024 * 1024),
                        "created_date": datetime.fromtimestamp(backup_file.stat().st_ctime).isoformat(),
                        "checksum": self._calculate_file_checksum(backup_file)
                    }
                    backups.append(backup_info)
                    self._register_backup(backup_info)
        except Exception as e:
            self.logger.error(f"Error discovering Docker backups: {e}")
        
        return backups
    
    def _calculate_directory_checksum(self, directory: Path) -> str:
        """Calculate checksum for entire directory"""
        hash_obj = hashlib.sha256()
        
        try:
            for file_path in sorted(directory.rglob("*")):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        hash_obj.update(f.read())
                    hash_obj.update(str(file_path).encode())
        except Exception as e:
            self.logger.error(f"Error calculating directory checksum: {e}")
            return "checksum_error"
        
        return hash_obj.hexdigest()[:16]  # Truncate for storage
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate checksum for a single file"""
        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
        except Exception as e:
            self.logger.error(f"Error calculating file checksum: {e}")
            return "checksum_error"
        
        return hash_obj.hexdigest()[:16]
    
    def _register_backup(self, backup_info: Dict[str, Any]):
        """Register backup in inventory database"""
        with sqlite3.connect(self.test_db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO backup_inventory 
                (timestamp, backup_path, backup_type, file_count, total_size_mb, 
                 checksum, created_date, verified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                backup_info["path"],
                backup_info["type"],
                backup_info["file_count"],
                backup_info["total_size_mb"],
                backup_info["checksum"],
                backup_info["created_date"],
                datetime.now().isoformat()
            ))
    
    def test_backup_integrity(self, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test backup integrity following TechTarget Step 9 guidelines"""
        self.logger.info(f"🔍 Testing integrity of backup: {backup_info['path']}")
        
        test_start = time.time()
        test_result = {
            "backup_path": backup_info["path"],
            "test_type": "integrity_check",
            "test_status": "RUNNING",
            "integrity_score": 0.0,
            "errors": []
        }
        
        try:
            # Verify checksum
            current_checksum = self._recalculate_checksum(backup_info)
            checksum_valid = current_checksum == backup_info["checksum"]
            
            if not checksum_valid:
                test_result["errors"].append(f"Checksum mismatch: expected {backup_info['checksum']}, got {current_checksum}")
            
            # Test file accessibility
            accessibility_score = self._test_file_accessibility(backup_info)
            
            # Test archive validity (if applicable)
            archive_valid = self._test_archive_validity(backup_info)
            
            # Calculate overall integrity score
            integrity_score = 0.0
            if checksum_valid:
                integrity_score += 0.4
            if accessibility_score > 0.8:
                integrity_score += 0.4
            if archive_valid:
                integrity_score += 0.2
            
            test_result.update({
                "test_status": "PASSED" if integrity_score > 0.8 else "FAILED",
                "integrity_score": integrity_score,
                "checksum_valid": checksum_valid,
                "accessibility_score": accessibility_score,
                "archive_valid": archive_valid,
                "duration_seconds": time.time() - test_start
            })
            
        except Exception as e:
            test_result.update({
                "test_status": "ERROR",
                "error_details": str(e),
                "duration_seconds": time.time() - test_start
            })
            self.logger.error(f"Integrity test error: {e}")
        
        self._record_test_result(test_result)
        return test_result
    
    def _recalculate_checksum(self, backup_info: Dict[str, Any]) -> str:
        """Recalculate checksum for comparison"""
        backup_path = Path(backup_info["path"])
        
        if backup_path.is_dir():
            return self._calculate_directory_checksum(backup_path)
        else:
            return self._calculate_file_checksum(backup_path)
    
    def _test_file_accessibility(self, backup_info: Dict[str, Any]) -> float:
        """Test file accessibility within backup"""
        backup_path = Path(backup_info["path"])
        accessible_files = 0
        total_files = 0
        
        try:
            if backup_path.is_dir():
                for file_path in backup_path.rglob("*"):
                    if file_path.is_file():
                        total_files += 1
                        try:
                            with open(file_path, 'rb') as f:
                                f.read(1024)  # Read first 1KB to test accessibility
                            accessible_files += 1
                        except:
                            pass
            else:
                total_files = 1
                try:
                    with open(backup_path, 'rb') as f:
                        f.read(1024)
                    accessible_files = 1
                except:
                    pass
        except Exception as e:
            self.logger.error(f"File accessibility test error: {e}")
            return 0.0
        
        return accessible_files / total_files if total_files > 0 else 0.0
    
    def _test_archive_validity(self, backup_info: Dict[str, Any]) -> bool:
        """Test validity of archive files"""
        backup_path = Path(backup_info["path"])
        
        try:
            if backup_path.suffix.lower() == '.gz' and backup_path.name.endswith('.tar.gz'):
                with tarfile.open(backup_path, 'r:gz') as tar:
                    # Try to list contents
                    members = tar.getmembers()
                    return len(members) > 0
            elif backup_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    # Test archive integrity
                    result = zip_file.testzip()
                    return result is None
            else:
                # Not an archive, consider valid
                return True
        except Exception as e:
            self.logger.error(f"Archive validity test error: {e}")
            return False
    
    def test_backup_restoration(self, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Test backup restoration following TechTarget Step 7 guidelines"""
        self.logger.info(f"🔄 Testing restoration of backup: {backup_info['path']}")
        
        test_start = time.time()
        test_result = {
            "backup_path": backup_info["path"],
            "test_type": "restoration_test",
            "test_status": "RUNNING",
            "restore_time_minutes": 0.0,
            "restoration_success": False,
            "errors": []
        }
        
        # Create isolated test environment
        test_dir = self.test_workspace / f"restore_test_{int(time.time())}"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Perform restoration based on backup type
            if backup_info["type"] == "docker_volume_backup":
                success = self._test_docker_volume_restoration(backup_info, test_dir)
            elif backup_info["type"] == "directory_backup":
                success = self._test_directory_restoration(backup_info, test_dir)
            else:
                success = self._test_generic_restoration(backup_info, test_dir)
            
            restore_time = (time.time() - test_start) / 60  # Convert to minutes
            
            # Validate restored data
            if success:
                validation_result = self._validate_restored_data(test_dir, backup_info)
                success = validation_result["valid"]
                if not success:
                    test_result["errors"].extend(validation_result["errors"])
            
            test_result.update({
                "test_status": "PASSED" if success else "FAILED",
                "restoration_success": success,
                "restore_time_minutes": restore_time,
                "duration_seconds": time.time() - test_start,
                "test_directory": str(test_dir)
            })
            
            # Check against RTO
            if restore_time > self.config["rto_target_minutes"]:
                test_result["errors"].append(f"Restore time {restore_time:.1f}m exceeds RTO target {self.config['rto_target_minutes']}m")
            
        except Exception as e:
            test_result.update({
                "test_status": "ERROR",
                "error_details": str(e),
                "duration_seconds": time.time() - test_start
            })
            self.logger.error(f"Restoration test error: {e}")
        
        finally:
            # Cleanup test directory
            try:
                shutil.rmtree(test_dir)
            except:
                pass
        
        self._record_test_result(test_result)
        return test_result
    
    def _test_docker_volume_restoration(self, backup_info: Dict[str, Any], test_dir: Path) -> bool:
        """Test Docker volume backup restoration"""
        try:
            backup_path = Path(backup_info["path"])
            
            # Extract tar.gz backup
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(test_dir)
            
            # Verify extraction
            extracted_files = list(test_dir.rglob("*"))
            return len(extracted_files) > 0
            
        except Exception as e:
            self.logger.error(f"Docker volume restoration test failed: {e}")
            return False
    
    def _test_directory_restoration(self, backup_info: Dict[str, Any], test_dir: Path) -> bool:
        """Test directory backup restoration"""
        try:
            backup_path = Path(backup_info["path"])
            
            # Copy directory contents
            for item in backup_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(backup_path)
                    dest_path = test_dir / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
            
            # Verify copy
            copied_files = list(test_dir.rglob("*"))
            return len(copied_files) > 0
            
        except Exception as e:
            self.logger.error(f"Directory restoration test failed: {e}")
            return False
    
    def _test_generic_restoration(self, backup_info: Dict[str, Any], test_dir: Path) -> bool:
        """Test generic backup restoration"""
        try:
            backup_path = Path(backup_info["path"])
            dest_path = test_dir / backup_path.name
            
            if backup_path.is_file():
                shutil.copy2(backup_path, dest_path)
                return dest_path.exists()
            else:
                shutil.copytree(backup_path, dest_path)
                return dest_path.exists()
                
        except Exception as e:
            self.logger.error(f"Generic restoration test failed: {e}")
            return False
    
    def _validate_restored_data(self, test_dir: Path, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate restored data integrity"""
        validation_result = {
            "valid": True,
            "errors": []
        }
        
        try:
            # Check file count
            restored_files = [f for f in test_dir.rglob("*") if f.is_file()]
            
            if len(restored_files) == 0:
                validation_result["valid"] = False
                validation_result["errors"].append("No files found in restoration")
                return validation_result
            
            # Sample file integrity check (check first few files)
            sample_size = min(10, len(restored_files))
            for i, file_path in enumerate(restored_files[:sample_size]):
                try:
                    # Try to read file
                    with open(file_path, 'rb') as f:
                        content = f.read(1024)
                        if len(content) == 0 and file_path.stat().st_size > 0:
                            validation_result["errors"].append(f"File {file_path.name} appears corrupted")
                except Exception as e:
                    validation_result["errors"].append(f"Cannot read file {file_path.name}: {e}")
            
            if validation_result["errors"]:
                validation_result["valid"] = False
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {e}")
        
        return validation_result
    
    def _record_test_result(self, test_result: Dict[str, Any]):
        """Record test result in database"""
        with sqlite3.connect(self.test_db) as conn:
            conn.execute("""
                INSERT INTO backup_tests (
                    timestamp, test_type, backup_source, test_status,
                    duration_seconds, restore_time_minutes, integrity_score,
                    test_notes, error_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                test_result.get("test_type", "unknown"),
                test_result.get("backup_path", "unknown"),
                test_result.get("test_status", "unknown"),
                test_result.get("duration_seconds", 0),
                test_result.get("restore_time_minutes", 0),
                test_result.get("integrity_score", 0),
                json.dumps(test_result.get("errors", [])),
                test_result.get("error_details", "")
            ))
    
    def run_comprehensive_backup_test(self) -> Dict[str, Any]:
        """Run comprehensive backup validation following TechTarget's guidelines"""
        self.logger.info("🧪 Starting comprehensive backup validation test")
        
        test_start = time.time()
        results = {
            "test_start": datetime.now().isoformat(),
            "backup_discovery": {},
            "integrity_tests": [],
            "restoration_tests": [],
            "performance_benchmarks": {},
            "summary": {}
        }
        
        try:
            # Step 1: Discover all backups
            backups = self.discover_backups()
            results["backup_discovery"] = {
                "total_backups": len(backups),
                "backup_types": list(set(b["type"] for b in backups)),
                "total_size_mb": sum(b["total_size_mb"] for b in backups)
            }
            
            # Step 2: Test backup integrity
            for backup in backups:
                integrity_result = self.test_backup_integrity(backup)
                results["integrity_tests"].append(integrity_result)
            
            # Step 3: Test restoration (sample of backups)
            test_samples = backups[:3]  # Test first 3 backups
            for backup in test_samples:
                restoration_result = self.test_backup_restoration(backup)
                results["restoration_tests"].append(restoration_result)
            
            # Step 4: Performance benchmarks
            results["performance_benchmarks"] = self._calculate_performance_benchmarks(results)
            
            # Step 5: Generate summary
            results["summary"] = self._generate_test_summary(results)
            results["test_duration_minutes"] = (time.time() - test_start) / 60
            
        except Exception as e:
            self.logger.error(f"Comprehensive test error: {e}")
            results["error"] = str(e)
        
        # Save results
        self._save_test_report(results)
        return results
    
    def _calculate_performance_benchmarks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance benchmarks"""
        benchmarks = {}
        
        try:
            # Restoration time analysis
            restore_times = [r.get("restore_time_minutes", 0) for r in results["restoration_tests"]]
            if restore_times:
                benchmarks["average_restore_time_minutes"] = sum(restore_times) / len(restore_times)
                benchmarks["max_restore_time_minutes"] = max(restore_times)
                benchmarks["rto_compliance"] = all(t <= self.config["rto_target_minutes"] for t in restore_times)
            
            # Integrity score analysis
            integrity_scores = [r.get("integrity_score", 0) for r in results["integrity_tests"]]
            if integrity_scores:
                benchmarks["average_integrity_score"] = sum(integrity_scores) / len(integrity_scores)
                benchmarks["min_integrity_score"] = min(integrity_scores)
                benchmarks["integrity_pass_rate"] = sum(1 for s in integrity_scores if s > 0.8) / len(integrity_scores)
            
        except Exception as e:
            self.logger.error(f"Benchmark calculation error: {e}")
        
        return benchmarks
    
    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        summary = {
            "overall_status": "PASSED",
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Check integrity test results
            failed_integrity = [r for r in results["integrity_tests"] if r["test_status"] != "PASSED"]
            if failed_integrity:
                summary["critical_issues"].append(f"{len(failed_integrity)} backups failed integrity tests")
                summary["overall_status"] = "FAILED"
            
            # Check restoration test results
            failed_restoration = [r for r in results["restoration_tests"] if r["test_status"] != "PASSED"]
            if failed_restoration:
                summary["critical_issues"].append(f"{len(failed_restoration)} backups failed restoration tests")
                summary["overall_status"] = "FAILED"
            
            # Check performance benchmarks
            benchmarks = results.get("performance_benchmarks", {})
            if not benchmarks.get("rto_compliance", True):
                summary["warnings"].append("Some backups exceed RTO targets")
            
            if benchmarks.get("average_integrity_score", 1.0) < 0.9:
                summary["warnings"].append("Average integrity score below 90%")
            
            # Generate recommendations
            if len(results["backup_discovery"]["backup_types"]) < 2:
                summary["recommendations"].append("Consider implementing redundant backup types")
            
            if benchmarks.get("average_restore_time_minutes", 0) > self.config["rto_target_minutes"] * 0.8:
                summary["recommendations"].append("Optimize backup size and compression for faster restoration")
            
        except Exception as e:
            self.logger.error(f"Summary generation error: {e}")
            summary["overall_status"] = "ERROR"
            summary["critical_issues"].append(f"Summary generation failed: {e}")
        
        return summary
    
    def _save_test_report(self, results: Dict[str, Any]):
        """Save comprehensive test report"""
        report_file = f"backup_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.logger.info(f"📊 Test report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save test report: {e}")

def main():
    """Main backup validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Memory System Backup Validator")
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive backup test')
    parser.add_argument('--discover', action='store_true', help='Discover and catalog backups')
    parser.add_argument('--integrity', action='store_true', help='Run integrity tests only')
    parser.add_argument('--restore', action='store_true', help='Run restoration tests only')
    
    args = parser.parse_args()
    
    validator = BackupValidator()
    
    if args.comprehensive:
        results = validator.run_comprehensive_backup_test()
        print(f"✅ Comprehensive test completed. Status: {results['summary']['overall_status']}")
        return
    
    if args.discover:
        backups = validator.discover_backups()
        print(f"📦 Discovered {len(backups)} backup sets")
        for backup in backups:
            print(f"   {backup['type']}: {backup['path']} ({backup['total_size_mb']:.1f} MB)")
        return
    
    if args.integrity:
        backups = validator.discover_backups()
        for backup in backups:
            result = validator.test_backup_integrity(backup)
            print(f"🔍 {backup['path']}: {result['test_status']} (Score: {result['integrity_score']:.2f})")
        return
    
    if args.restore:
        backups = validator.discover_backups()
        for backup in backups[:2]:  # Test first 2
            result = validator.test_backup_restoration(backup)
            print(f"🔄 {backup['path']}: {result['test_status']} ({result['restore_time_minutes']:.1f}m)")
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main() 