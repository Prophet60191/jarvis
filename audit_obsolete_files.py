#!/usr/bin/env python3
"""
JARVIS Obsolete Files Audit
Comprehensive audit to identify documentation, scripts, and tests that are no longer needed
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

def analyze_test_files():
    """Analyze test files for obsolete or redundant tests."""
    
    obsolete_tests = {
        'root_level_tests': [],
        'duplicate_tests': [],
        'consciousness_tests': [],
        'orchestration_tests': [],
        'debug_scripts': [],
        'temporary_tests': []
    }
    
    # Root level test files (should be in tests/ directory)
    root_test_files = [
        'test_*.py', 'debug_*.py', 'final_*.py', 'additional_*.py',
        'analyze_*.py', 'benchmark_*.py', 'run_*.py'
    ]
    
    root_path = Path('.')
    for pattern in ['test_*.py', 'debug_*.py', 'final_*.py']:
        for file in root_path.glob(pattern):
            if file.is_file():
                obsolete_tests['root_level_tests'].append(str(file))
    
    # Consciousness system tests (may be obsolete if we make it optional)
    consciousness_keywords = [
        'consciousness', 'self_awareness', 'architectural',
        'semantic', 'dependency_analyzer'
    ]

    for file in root_path.rglob('*.py'):
        if any(keyword in file.name.lower() for keyword in consciousness_keywords):
            if 'test' in file.name.lower() or 'debug' in file.name.lower():
                obsolete_tests['consciousness_tests'].append(str(file))
    
    # Orchestration system tests (may be simplified)
    orchestration_keywords = [
        'orchestration', 'workflow', 'routing', 'enhanced'
    ]

    for file in root_path.rglob('*.py'):
        if any(keyword in file.name.lower() for keyword in orchestration_keywords):
            if 'test' in file.name.lower() or 'debug' in file.name.lower():
                obsolete_tests['orchestration_tests'].append(str(file))
    
    # Debug and temporary scripts
    debug_patterns = [
        'debug_*.py', 'test_*_fix*.py', 'fix_*.py', 'cleanup_*.py',
        'demo_*.py', 'verify_*.py', 'diagnose_*.py'
    ]
    
    for pattern in debug_patterns:
        for file in root_path.glob(pattern):
            if file.is_file():
                obsolete_tests['debug_scripts'].append(str(file))
    
    # Temporary test files
    temp_patterns = [
        'test_*_temp*.py', 'test_*_old*.py', 'test_*_backup*.py',
        '*_temp.py', '*_old.py', '*_backup.py'
    ]
    
    for pattern in temp_patterns:
        for file in root_path.rglob(pattern):
            if file.is_file():
                obsolete_tests['temporary_tests'].append(str(file))
    
    return obsolete_tests

def analyze_documentation():
    """Analyze documentation for obsolete or redundant docs."""
    
    obsolete_docs = {
        'implementation_docs': [],
        'consciousness_docs': [],
        'orchestration_docs': [],
        'duplicate_guides': [],
        'outdated_specs': [],
        'migration_docs': []
    }
    
    root_path = Path('.')
    
    # Implementation and specification docs (may be outdated)
    impl_patterns = [
        '*IMPLEMENTATION*', '*SPECIFICATION*', '*ENHANCED*',
        '*INTEGRATION*', '*MIGRATION*', '*PHASE*'
    ]
    
    for pattern in impl_patterns:
        for file in root_path.glob(f'{pattern}.md'):
            if file.is_file():
                obsolete_docs['implementation_docs'].append(str(file))
    
    # Consciousness system documentation
    consciousness_keywords = [
        'CONSCIOUSNESS', 'SELF_AWARENESS', 'ARCHITECTURAL'
    ]

    for file in root_path.rglob('*.md'):
        if any(keyword in file.name.upper() for keyword in consciousness_keywords):
            obsolete_docs['consciousness_docs'].append(str(file))
    
    # Orchestration system documentation
    orchestration_keywords = [
        'ORCHESTRATION', 'ROUTING', 'WORKFLOW', 'ENHANCED'
    ]

    for file in root_path.rglob('*.md'):
        if any(keyword in file.name.upper() for keyword in orchestration_keywords):
            obsolete_docs['orchestration_docs'].append(str(file))
    
    # Duplicate guides
    guide_patterns = [
        'GUIDE.md', 'USER_GUIDE.md', 'GETTING_STARTED*.md',
        'QUICK_START*.md', 'TROUBLESHOOTING*.md'
    ]
    
    guides_found = []
    for pattern in guide_patterns:
        for file in root_path.rglob(pattern):
            guides_found.append(str(file))
    
    # Check for duplicates
    guide_types = {}
    for guide in guides_found:
        guide_type = Path(guide).stem.lower()
        if 'guide' in guide_type or 'start' in guide_type:
            key = 'user_guides'
        elif 'troubleshoot' in guide_type:
            key = 'troubleshooting'
        else:
            key = 'other'
        
        if key not in guide_types:
            guide_types[key] = []
        guide_types[key].append(guide)
    
    for guide_type, files in guide_types.items():
        if len(files) > 1:
            obsolete_docs['duplicate_guides'].extend(files[1:])  # Keep first, mark others as duplicates
    
    return obsolete_docs

def analyze_scripts():
    """Analyze scripts for obsolete or redundant functionality."""
    
    obsolete_scripts = {
        'setup_scripts': [],
        'migration_scripts': [],
        'debug_scripts': [],
        'test_runners': [],
        'deployment_scripts': [],
        'cleanup_scripts': []
    }
    
    root_path = Path('.')
    
    # Setup and installation scripts
    setup_patterns = [
        'setup_*.py', 'install_*.py', 'deploy_*.py', 'build_*.py'
    ]
    
    for pattern in setup_patterns:
        for file in root_path.rglob(pattern):
            if file.is_file():
                obsolete_scripts['setup_scripts'].append(str(file))
    
    # Migration scripts
    migration_patterns = [
        'migrate_*.py', 'migration_*.py', 'update_*.py'
    ]
    
    for pattern in migration_patterns:
        for file in root_path.rglob(pattern):
            if file.is_file():
                obsolete_scripts['migration_scripts'].append(str(file))
    
    # Debug and diagnostic scripts
    debug_patterns = [
        'debug_*.py', 'diagnose_*.py', 'check_*.py', 'verify_*.py'
    ]
    
    for pattern in debug_patterns:
        for file in root_path.glob(pattern):
            if file.is_file():
                obsolete_scripts['debug_scripts'].append(str(file))
    
    # Test runners and benchmarks
    test_patterns = [
        'run_*.py', 'benchmark_*.py', 'test_*.py'
    ]
    
    for pattern in test_patterns:
        for file in root_path.glob(pattern):
            if file.is_file() and 'test' in file.name:
                obsolete_scripts['test_runners'].append(str(file))
    
    # Cleanup scripts
    cleanup_patterns = [
        'cleanup_*.py', 'clean_*.py', 'remove_*.py', 'delete_*.py'
    ]
    
    for pattern in cleanup_patterns:
        for file in root_path.glob(pattern):
            if file.is_file():
                obsolete_scripts['cleanup_scripts'].append(str(file))
    
    return obsolete_scripts

def analyze_data_directories():
    """Analyze data directories for obsolete or test data."""
    
    obsolete_data = {
        'test_data': [],
        'backup_data': [],
        'temp_data': [],
        'benchmark_data': [],
        'old_configs': []
    }
    
    data_path = Path('data')
    if data_path.exists():
        # Test data directories
        for item in data_path.iterdir():
            if item.is_dir() and ('test' in item.name or 'temp' in item.name):
                obsolete_data['test_data'].append(str(item))
        
        # Backup directories
        backup_dirs = ['backups', 'test_backups']
        for backup_dir in backup_dirs:
            backup_path = data_path / backup_dir
            if backup_path.exists():
                obsolete_data['backup_data'].append(str(backup_path))
    
    # Benchmark results
    benchmark_path = Path('benchmark_results')
    if benchmark_path.exists():
        obsolete_data['benchmark_data'].append(str(benchmark_path))
    
    # Old configuration files
    config_patterns = ['*.json', '*.yaml', '*.yml']
    for pattern in config_patterns:
        for file in Path('.').glob(pattern):
            if any(keyword in file.name.lower() for keyword in ['old', 'backup', 'temp', 'test']):
                obsolete_data['old_configs'].append(str(file))
    
    return obsolete_data

def analyze_app_directories():
    """Analyze application directories for test/demo apps."""
    
    obsolete_apps = {
        'test_apps': [],
        'demo_apps': [],
        'incomplete_apps': []
    }
    
    # Root level app directories
    app_patterns = ['*_app', '*app*', 'test_*', 'demo_*']
    
    for pattern in app_patterns:
        for item in Path('.').glob(pattern):
            if item.is_dir():
                if 'test' in item.name.lower():
                    obsolete_apps['test_apps'].append(str(item))
                elif 'demo' in item.name.lower():
                    obsolete_apps['demo_apps'].append(str(item))
                elif any(keyword in item.name.lower() for keyword in ['button', 'color', 'calculator']):
                    obsolete_apps['demo_apps'].append(str(item))
    
    # Check apps directory
    apps_path = Path('apps')
    if apps_path.exists():
        for app_dir in apps_path.iterdir():
            if app_dir.is_dir():
                # Check if app is incomplete or test-only
                if not (app_dir / 'README.md').exists() or not (app_dir / 'main.py').exists():
                    obsolete_apps['incomplete_apps'].append(str(app_dir))
    
    return obsolete_apps

def generate_cleanup_recommendations():
    """Generate specific cleanup recommendations."""
    
    recommendations = {
        'immediate_removal': {
            'description': 'Files that can be safely removed immediately',
            'categories': [
                'Debug scripts in root directory',
                'Temporary test files',
                'Old backup files',
                'Benchmark result files',
                'Demo applications'
            ]
        },
        'conditional_removal': {
            'description': 'Files to remove if implementing simplified architecture',
            'categories': [
                'Consciousness system tests and docs',
                'Complex orchestration tests',
                'Enhanced system documentation',
                'Migration scripts'
            ]
        },
        'consolidation': {
            'description': 'Files that should be consolidated',
            'categories': [
                'Multiple user guides',
                'Duplicate documentation',
                'Scattered test files',
                'Multiple setup scripts'
            ]
        },
        'organization': {
            'description': 'Files that should be moved to proper locations',
            'categories': [
                'Root-level test files → tests/',
                'Root-level debug scripts → scripts/debug/',
                'Documentation → docs/',
                'Configuration files → config/'
            ]
        }
    }
    
    return recommendations

def main():
    """Run comprehensive obsolete files audit."""
    
    print("🔍 JARVIS OBSOLETE FILES AUDIT")
    print("=" * 60)
    
    # Run all analyses
    print("\n📋 Analyzing test files...")
    obsolete_tests = analyze_test_files()
    
    print("📋 Analyzing documentation...")
    obsolete_docs = analyze_documentation()
    
    print("📋 Analyzing scripts...")
    obsolete_scripts = analyze_scripts()
    
    print("📋 Analyzing data directories...")
    obsolete_data = analyze_data_directories()
    
    print("📋 Analyzing app directories...")
    obsolete_apps = analyze_app_directories()
    
    # Generate report
    print(f"\n📊 AUDIT RESULTS")
    print("-" * 30)
    
    total_obsolete = 0
    
    print(f"\n🧪 OBSOLETE TESTS:")
    for category, files in obsolete_tests.items():
        if files:
            print(f"  {category.replace('_', ' ').title()}: {len(files)} files")
            total_obsolete += len(files)
            for file in files[:3]:  # Show first 3
                print(f"    • {file}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
    
    print(f"\n📚 OBSOLETE DOCUMENTATION:")
    for category, files in obsolete_docs.items():
        if files:
            print(f"  {category.replace('_', ' ').title()}: {len(files)} files")
            total_obsolete += len(files)
            for file in files[:3]:
                print(f"    • {file}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
    
    print(f"\n🔧 OBSOLETE SCRIPTS:")
    for category, files in obsolete_scripts.items():
        if files:
            print(f"  {category.replace('_', ' ').title()}: {len(files)} files")
            total_obsolete += len(files)
            for file in files[:3]:
                print(f"    • {file}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")
    
    print(f"\n💾 OBSOLETE DATA:")
    for category, items in obsolete_data.items():
        if items:
            print(f"  {category.replace('_', ' ').title()}: {len(items)} items")
            total_obsolete += len(items)
            for item in items[:3]:
                print(f"    • {item}")
            if len(items) > 3:
                print(f"    ... and {len(items) - 3} more")
    
    print(f"\n📱 OBSOLETE APPS:")
    for category, apps in obsolete_apps.items():
        if apps:
            print(f"  {category.replace('_', ' ').title()}: {len(apps)} apps")
            total_obsolete += len(apps)
            for app in apps[:3]:
                print(f"    • {app}")
            if len(apps) > 3:
                print(f"    ... and {len(apps) - 3} more")
    
    print(f"\n📊 SUMMARY:")
    print(f"Total obsolete files/directories identified: {total_obsolete}")
    
    # Generate recommendations
    print(f"\n💡 CLEANUP RECOMMENDATIONS:")
    recommendations = generate_cleanup_recommendations()
    
    for rec_type, details in recommendations.items():
        print(f"\n{rec_type.replace('_', ' ').upper()}:")
        print(f"  {details['description']}")
        for category in details['categories']:
            print(f"    • {category}")
    
    # Save detailed results
    results = {
        'audit_date': datetime.now().isoformat(),
        'total_obsolete_files': total_obsolete,
        'obsolete_tests': obsolete_tests,
        'obsolete_docs': obsolete_docs,
        'obsolete_scripts': obsolete_scripts,
        'obsolete_data': obsolete_data,
        'obsolete_apps': obsolete_apps,
        'recommendations': recommendations
    }
    
    with open('obsolete_files_audit.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: obsolete_files_audit.json")

    # Generate cleanup script
    print(f"\n🔧 NEXT STEPS:")
    print("1. Review the cleanup plan: OBSOLETE_FILES_CLEANUP_PLAN.md")
    print("2. Run the cleanup script: python cleanup_obsolete_files.py")
    print("3. Test functionality after each cleanup phase")
    print("4. Implement complexity reduction recommendations")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
