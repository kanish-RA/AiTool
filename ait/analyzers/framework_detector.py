"""Framework detection for web applications"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Any
from ..core.base import BaseAnalyzer

class FrameworkDetector(BaseAnalyzer):
    """Detects web frameworks and technologies in a codebase"""
    
    def __init__(self, name: str = "FrameworkDetector"):
        super().__init__(name)
        
        # Framework detection rules
        self.detection_rules = {
            'React': {
                'files': ['package.json'],
                'dependencies': ['react', 'react-dom'],
                'file_patterns': ['.jsx', '.tsx'],
                'content_patterns': ['import React', 'from "react"']
            },
            'Vue.js': {
                'files': ['package.json'],
                'dependencies': ['vue'],
                'file_patterns': ['.vue'],
                'content_patterns': ['<template>', 'Vue.component']
            },
            'Angular': {
                'files': ['package.json', 'angular.json'],
                'dependencies': ['@angular/core'],
                'file_patterns': ['.component.ts'],
                'content_patterns': ['@Component', '@NgModule']
            },
            'Django': {
                'files': ['manage.py', 'settings.py', 'requirements.txt'],
                'dependencies': ['django'],
                'file_patterns': ['.html'],
                'content_patterns': ['{% load', '{{ ', 'django.']
            },
            'Flask': {
                'files': ['app.py', 'requirements.txt'],
                'dependencies': ['flask'],
                'content_patterns': ['from flask import', '@app.route']
            },
            'Express.js': {
                'files': ['package.json'],
                'dependencies': ['express'],
                'content_patterns': ['require("express")', 'app.listen(']
            },
            'Laravel': {
                'files': ['composer.json', 'artisan'],
                'dependencies': ['laravel/framework'],
                'file_patterns': ['.blade.php'],
                'content_patterns': ['@extends', '@section']
            },
            'Spring Boot': {
                'files': ['pom.xml', 'build.gradle'],
                'content_patterns': ['spring-boot-starter', '@SpringBootApplication']
            }
        }
    
    def can_analyze(self, file_path: Path) -> bool:
        """Can analyze any directory or specific framework files"""
        if file_path.is_dir():
            return True
        
        # Check if it's a framework-specific file
        file_name = file_path.name.lower()
        for framework, rules in self.detection_rules.items():
            if file_name in rules.get('files', []):
                return True
        
        return False
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze directory or file for framework detection"""
        if file_path.is_dir():
            return self._analyze_directory(file_path)
        else:
            return self._analyze_file(file_path)
    
    def _analyze_directory(self, directory: Path) -> Dict[str, Any]:
        """Analyze entire directory for frameworks"""
        detected_frameworks = set()
        evidence = {}
        file_count = 0
        
        # Walk through directory
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
            
            for file in files:
                file_path = Path(root) / file
                file_count += 1
                
                # Check each framework
                for framework, rules in self.detection_rules.items():
                    framework_evidence = self._check_file_for_framework(file_path, framework, rules)
                    if framework_evidence['detected']:
                        detected_frameworks.add(framework)
                        if framework not in evidence:
                            evidence[framework] = []
                        evidence[framework].extend(framework_evidence['evidence'])
        
        return {
            'type': 'directory_analysis',
            'frameworks_detected': list(detected_frameworks),
            'evidence': evidence,
            'files_scanned': file_count,
            'confidence': self._calculate_confidence(evidence)
        }
    
    def _analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze single file for framework indicators"""
        detected_frameworks = set()
        evidence = {}
        
        for framework, rules in self.detection_rules.items():
            framework_evidence = self._check_file_for_framework(file_path, framework, rules)
            if framework_evidence['detected']:
                detected_frameworks.add(framework)
                evidence[framework] = framework_evidence['evidence']
        
        return {
            'type': 'file_analysis',
            'file': str(file_path),
            'frameworks_detected': list(detected_frameworks),
            'evidence': evidence
        }
    
    def _check_file_for_framework(self, file_path: Path, framework: str, rules: Dict) -> Dict[str, Any]:
        """Check if a file indicates a specific framework"""
        evidence = []
        detected = False
        
        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()
        
        try:
            # Check if it's a framework-specific file
            if file_name in rules.get('files', []):
                evidence.append(f"Framework file: {file_name}")
                detected = True
                
                # For package.json, check dependencies
                if file_name == 'package.json':
                    deps_evidence = self._check_package_json(file_path, rules.get('dependencies', []))
                    evidence.extend(deps_evidence)
                    if deps_evidence:
                        detected = True
                
                # For requirements.txt, check Python dependencies
                elif file_name == 'requirements.txt':
                    deps_evidence = self._check_requirements_txt(file_path, rules.get('dependencies', []))
                    evidence.extend(deps_evidence)
                    if deps_evidence:
                        detected = True
                
                # For composer.json, check PHP dependencies
                elif file_name == 'composer.json':
                    deps_evidence = self._check_composer_json(file_path, rules.get('dependencies', []))
                    evidence.extend(deps_evidence)
                    if deps_evidence:
                        detected = True
            
            # Check file extension patterns
            if file_ext in rules.get('file_patterns', []):
                evidence.append(f"File pattern: {file_ext}")
                detected = True
            
            # Check content patterns
            content_evidence = self._check_file_content(file_path, rules.get('content_patterns', []))
            if content_evidence:
                evidence.extend(content_evidence)
                detected = True
        
        except Exception as e:
            # If we can't read the file, just skip it
            pass
        
        return {
            'detected': detected,
            'evidence': evidence
        }
    
    def _check_package_json(self, file_path: Path, target_deps: List[str]) -> List[str]:
        """Check package.json for specific dependencies"""
        evidence = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
                
                all_deps = {}
                all_deps.update(data.get('dependencies', {}))
                all_deps.update(data.get('devDependencies', {}))
                
                for dep in target_deps:
                    if dep in all_deps:
                        evidence.append(f"Dependency: {dep}")
        
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        return evidence
    
    def _check_requirements_txt(self, file_path: Path, target_deps: List[str]) -> List[str]:
        """Check requirements.txt for Python dependencies"""
        evidence = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                
                for dep in target_deps:
                    if dep.lower() in content:
                        evidence.append(f"Python dependency: {dep}")
        
        except FileNotFoundError:
            pass
        
        return evidence
    
    def _check_composer_json(self, file_path: Path, target_deps: List[str]) -> List[str]:
        """Check composer.json for PHP dependencies"""
        evidence = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
                
                all_deps = {}
                all_deps.update(data.get('require', {}))
                all_deps.update(data.get('require-dev', {}))
                
                for dep in target_deps:
                    if dep in all_deps:
                        evidence.append(f"PHP dependency: {dep}")
        
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        
        return evidence
    
    def _check_file_content(self, file_path: Path, patterns: List[str]) -> List[str]:
        """Check file content for specific patterns"""
        evidence = []
        
        # Only check text files and limit size
        if file_path.stat().st_size > 1000000:  # Skip files > 1MB
            return evidence
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for pattern in patterns:
                    if pattern in content:
                        evidence.append(f"Content pattern: {pattern}")
        
        except (UnicodeDecodeError, FileNotFoundError, PermissionError):
            pass
        
        return evidence
    
    def _calculate_confidence(self, evidence: Dict[str, List[str]]) -> Dict[str, float]:
        """Calculate confidence score for each detected framework"""
        confidence = {}
        
        for framework, evidences in evidence.items():
            # Simple confidence calculation based on evidence count
            score = min(len(evidences) * 0.25, 1.0)  # Max confidence is 1.0
            confidence[framework] = round(score, 2)
        
        return confidence