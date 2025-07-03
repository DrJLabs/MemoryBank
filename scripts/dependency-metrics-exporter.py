#!/usr/bin/env python3
"""
Dependency Metrics Exporter for Prometheus

This script scans the MemoryBank monorepo for dependency information
and exports metrics in Prometheus format.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Metrics definitions
vulnerability_metrics = {
    'critical': Gauge('dependency_vulnerabilities_critical_total', 'Number of critical vulnerabilities'),
    'high': Gauge('dependency_vulnerabilities_high_total', 'Number of high vulnerabilities'),
    'medium': Gauge('dependency_vulnerabilities_medium_total', 'Number of medium vulnerabilities'),
    'low': Gauge('dependency_vulnerabilities_low_total', 'Number of low vulnerabilities'),
}

dependency_metrics = {
    'total': Gauge('dependency_packages_total', 'Total number of dependencies'),
    'outdated': Gauge('dependency_packages_outdated_total', 'Number of outdated dependencies'),
    'up_to_date': Gauge('dependency_packages_up_to_date_total', 'Number of up-to-date dependencies'),
    'by_ecosystem': Gauge('dependency_packages_by_ecosystem', 'Dependencies by ecosystem', ['ecosystem']),
}

build_metrics = {
    'total': Counter('build_total', 'Total number of builds'),
    'success': Counter('build_success_total', 'Number of successful builds'),
    'failure': Counter('build_failure_total', 'Number of failed builds'),
}

update_metrics = {
    'total': Counter('dependency_updates_total', 'Total number of dependency updates'),
    'duration': Histogram('dependency_update_duration_seconds', 'Time taken to update dependencies'),
}


class DependencyScanner:
    """Scans the monorepo for dependency information"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.python_projects = [
            '.',
            'custom-gpt-adapter',
            'mem0',
            'mem0/embedchain',
            'mem0/openmemory',
        ]
        self.js_projects = [
            'mem0/mem0-ts',
            'mem0/vercel-ai-sdk',
            'mem0/openmemory/ui',
            'mem0/examples/mem0-demo',
        ]
    
    def scan_python_vulnerabilities(self) -> Dict[str, int]:
        """Scan Python projects for vulnerabilities using safety"""
        vulnerabilities = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for project in self.python_projects:
            project_path = self.repo_root / project
            if not (project_path / 'pyproject.toml').exists():
                continue
            
            try:
                # Export requirements
                subprocess.run(
                    ['poetry', 'export', '-f', 'requirements.txt', '--without-hashes', '-o', 'temp-requirements.txt'],
                    cwd=project_path,
                    capture_output=True,
                    check=True
                )
                
                # Run safety check
                result = subprocess.run(
                    ['safety', 'check', '-r', 'temp-requirements.txt', '--json'],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    data = json.loads(result.stdout)
                    for vuln in data.get('vulnerabilities', []):
                        severity = vuln.get('severity', 'low').lower()
                        if severity in vulnerabilities:
                            vulnerabilities[severity] += 1
                
                # Cleanup
                (project_path / 'temp-requirements.txt').unlink(missing_ok=True)
                
            except Exception as e:
                print(f"Error scanning {project}: {e}")
        
        return vulnerabilities
    
    def scan_js_vulnerabilities(self) -> Dict[str, int]:
        """Scan JavaScript projects for vulnerabilities using npm audit"""
        vulnerabilities = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for project in self.js_projects:
            project_path = self.repo_root / project
            if not (project_path / 'package.json').exists():
                continue
            
            try:
                result = subprocess.run(
                    ['npm', 'audit', '--json'],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    data = json.loads(result.stdout)
                    for severity, count in data.get('metadata', {}).get('vulnerabilities', {}).items():
                        if severity.lower() in vulnerabilities:
                            vulnerabilities[severity.lower()] += count
                
            except Exception as e:
                print(f"Error scanning {project}: {e}")
        
        return vulnerabilities
    
    def count_dependencies(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Count total dependencies and by ecosystem"""
        total_deps = 0
        by_ecosystem = {'python': 0, 'javascript': 0}
        outdated = 0
        
        # Count Python dependencies
        for project in self.python_projects:
            project_path = self.repo_root / project
            if (project_path / 'pyproject.toml').exists():
                try:
                    with open(project_path / 'pyproject.toml', 'r') as f:
                        content = f.read()
                        # Simple count of dependencies (more sophisticated parsing could be added)
                        deps = content.count('=')
                        by_ecosystem['python'] += deps
                        total_deps += deps
                except Exception as e:
                    print(f"Error counting Python deps in {project}: {e}")
        
        # Count JavaScript dependencies
        for project in self.js_projects:
            project_path = self.repo_root / project
            if (project_path / 'package.json').exists():
                try:
                    with open(project_path / 'package.json', 'r') as f:
                        data = json.load(f)
                        deps = len(data.get('dependencies', {})) + len(data.get('devDependencies', {}))
                        by_ecosystem['javascript'] += deps
                        total_deps += deps
                except Exception as e:
                    print(f"Error counting JS deps in {project}: {e}")
        
        # Estimate outdated (this is a placeholder - real implementation would check actual versions)
        outdated = int(total_deps * 0.15)  # Assume 15% are outdated
        
        return {
            'total': total_deps,
            'outdated': outdated,
            'up_to_date': total_deps - outdated
        }, by_ecosystem


def update_metrics(scanner: DependencyScanner):
    """Update all metrics"""
    print("Updating dependency metrics...")
    
    # Update vulnerability metrics
    python_vulns = scanner.scan_python_vulnerabilities()
    js_vulns = scanner.scan_js_vulnerabilities()
    
    for severity in ['critical', 'high', 'medium', 'low']:
        total = python_vulns.get(severity, 0) + js_vulns.get(severity, 0)
        vulnerability_metrics[severity].set(total)
    
    # Update dependency count metrics
    counts, by_ecosystem = scanner.count_dependencies()
    dependency_metrics['total'].set(counts['total'])
    dependency_metrics['outdated'].set(counts['outdated'])
    dependency_metrics['up_to_date'].set(counts['up_to_date'])
    
    for ecosystem, count in by_ecosystem.items():
        dependency_metrics['by_ecosystem'].labels(ecosystem=ecosystem).set(count)
    
    # Simulate build metrics (in real implementation, these would come from CI/CD)
    build_metrics['total'].inc()
    if counts['total'] > 0:  # Simple success condition
        build_metrics['success'].inc()
    else:
        build_metrics['failure'].inc()
    
    print("Metrics updated successfully")


def main():
    """Main function"""
    # Determine repository root
    repo_root = Path(__file__).parent.parent
    
    # Initialize scanner
    scanner = DependencyScanner(repo_root)
    
    # Start Prometheus metrics server
    port = int(os.environ.get('METRICS_PORT', '9091'))
    start_http_server(port)
    print(f"Metrics server started on port {port}")
    
    # Update metrics every 5 minutes
    while True:
        try:
            update_metrics(scanner)
        except Exception as e:
            print(f"Error updating metrics: {e}")
        
        time.sleep(300)  # 5 minutes


if __name__ == '__main__':
    main() 