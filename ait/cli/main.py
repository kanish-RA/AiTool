"""Main CLI entry point"""

import click
import sys
from pathlib import Path
from typing import List, Optional
import json

# Import our framework components
import ait
from ait.analyzers import FrameworkDetector, HTMLAnalyzer
from ait.generators import GherkinGenerator
from ait.ai import OllamaProvider

@click.group()
@click.version_option(version=ait.__version__)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
def cli(verbose, config):
    """🤖 AI Testing Framework - Intelligent test automation for any web application"""
    
    # Set verbose mode in global config
    ait.config.set('verbose', verbose)
    
    if verbose:
        click.echo("🔧 Verbose mode enabled")
    
    if config:
        click.echo(f"📁 Loading config from: {config}")
        # TODO: Load config file
    
    # Show welcome message
    if verbose:
        click.echo("🚀 AI Testing Framework initialized")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for analysis results')
@click.option('--format', '-f', type=click.Choice(['json', 'summary']), default='summary', help='Output format')
def analyze(path, output, format):
    """📊 Analyze codebase and extract testable elements"""
    
    click.echo(f"🔍 Analyzing: {path}")
    
    path_obj = Path(path)
    
    # Initialize analyzers
    framework_detector = FrameworkDetector()
    html_analyzer = HTMLAnalyzer()
    
    results = []
    
    if path_obj.is_file():
        # Analyze single file
        results = analyze_single_file(path_obj, framework_detector, html_analyzer)
    else:
        # Analyze directory
        results = analyze_directory(path_obj, framework_detector, html_analyzer)
    
    # Output results
    if format == 'json':
        output_json(results, output)
    else:
        output_summary(results, output)
    
    click.echo(f"✅ Analysis complete! Found {len(results)} files")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for generated scenarios')
@click.option('--no-ai', is_flag=True, help='Disable AI generation, use rule-based only')
@click.option('--format', '-f', type=click.Choice(['gherkin', 'json']), default='gherkin', help='Output format')
def generate(path, output, no_ai, format):
    """🥒 Generate Gherkin test scenarios from codebase analysis"""
    
    click.echo(f"🥒 Generating scenarios for: {path}")
    
    # First analyze the codebase
    with click.progressbar(label='Analyzing codebase') as bar:
        path_obj = Path(path)
        framework_detector = FrameworkDetector()
        html_analyzer = HTMLAnalyzer()
        
        if path_obj.is_file():
            analysis_results = analyze_single_file(path_obj, framework_detector, html_analyzer)
        else:
            analysis_results = analyze_directory(path_obj, framework_detector, html_analyzer)
        bar.update(1)
    
    if not analysis_results:
        click.echo("❌ No analyzable files found!")
        sys.exit(1)
    
    # Generate scenarios
    with click.progressbar(label='Generating scenarios') as bar:
        gherkin_generator = GherkinGenerator()
        
        generation_options = {'use_ai': not no_ai}
        result = gherkin_generator.generate(analysis_results, generation_options)
        bar.update(1)
    
    # Output results
    if format == 'json':
        output_data = json.dumps(result, indent=2)
    else:
        output_data = result['content']
    
    if output:
        with open(output, 'w') as f:
            f.write(output_data)
        click.echo(f"📝 Scenarios written to: {output}")
    else:
        click.echo("\n" + "="*60)
        click.echo(output_data)
        click.echo("="*60)
    
    # Show summary
    click.echo(f"✅ Generated {result['scenarios_count']} scenarios using {result['generation_method']}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def detect(path):
    """🕵️ Detect web frameworks in codebase"""
    
    click.echo(f"🔍 Detecting frameworks in: {path}")
    
    framework_detector = FrameworkDetector()
    path_obj = Path(path)
    
    if path_obj.is_file():
        click.echo("❌ Framework detection requires a directory, not a single file")
        sys.exit(1)
    
    result = framework_detector.analyze(path_obj)
    
    if 'error' in result:
        click.echo(f"❌ Error: {result['error']}")
        sys.exit(1)
    
    frameworks = result['frameworks_detected']
    
    if frameworks:
        click.echo(f"🎯 Detected Frameworks:")
        for framework in frameworks:
            confidence = result['confidence'].get(framework, 0)
            click.echo(f"  ✅ {framework} (confidence: {confidence})")
        
        click.echo(f"\n📊 Evidence Summary:")
        for framework, evidence_list in result['evidence'].items():
            click.echo(f"  {framework}:")
            for evidence in evidence_list[:3]:  # Show first 3
                click.echo(f"    - {evidence}")
            if len(evidence_list) > 3:
                click.echo(f"    ... and {len(evidence_list) - 3} more")
    else:
        click.echo("❌ No specific frameworks detected")
        click.echo("💡 This appears to be a generic web application")
    
    click.echo(f"\n📁 Scanned {result['files_scanned']} files")

@cli.command()
def status():
    """🔧 Show framework status and configuration"""
    
    click.echo("🔧 AI Testing Framework Status")
    click.echo("=" * 40)
    
    # Framework info
    click.echo(f"Version: {ait.__version__}")
    
    # Configuration
    click.echo(f"\n⚙️ Configuration:")
    click.echo(f"  Verbose: {ait.config.get('verbose')}")
    click.echo(f"  AI Enabled: {ait.config.get('ai_enabled')}")
    click.echo(f"  Max File Size: {ait.config.get('max_file_size')} bytes")
    
    # AI Provider Status
    click.echo(f"\n🤖 AI Provider Status:")
    ai_provider = OllamaProvider()
    if ai_provider.is_available():
        click.echo(f"  ✅ Ollama: Available ({ai_provider.model})")
    else:
        click.echo(f"  ❌ Ollama: Not available")
        click.echo(f"  💡 Start with: ollama serve")
    
    # Registry Status
    click.echo(f"\n📋 Registered Components:")
    click.echo(f"  Analyzers: {len(ait.registry.list_analyzers())}")
    click.echo(f"  Available: {', '.join(ait.registry.list_analyzers())}")

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--analyzer', '-a', type=click.Choice(['framework', 'html']), default='html', help='Analyzer to use')
def inspect(path, analyzer):
    """🔎 Inspect specific file with detailed output"""
    
    path_obj = Path(path)
    
    if not path_obj.is_file():
        click.echo("❌ Inspect command requires a single file")
        sys.exit(1)
    
    click.echo(f"🔎 Inspecting: {path_obj.name}")
    click.echo(f"📏 Size: {path_obj.stat().st_size} bytes")
    
    if analyzer == 'framework':
        detector = FrameworkDetector()
        if detector.can_analyze(path_obj):
            result = detector.analyze(path_obj)
            display_framework_result(result)
        else:
            click.echo("❌ Framework detector cannot analyze this file")
    
    elif analyzer == 'html':
        html_analyzer = HTMLAnalyzer()
        if html_analyzer.can_analyze(path_obj):
            result = html_analyzer.analyze(path_obj)
            display_html_result(result)
        else:
            click.echo("❌ HTML analyzer cannot analyze this file (not HTML)")

# Helper functions
def analyze_single_file(file_path: Path, framework_detector: FrameworkDetector, html_analyzer: HTMLAnalyzer) -> List:
    """Analyze a single file"""
    results = []
    
    if framework_detector.can_analyze(file_path):
        result = framework_detector.analyze(file_path)
        results.append(result)
    
    if html_analyzer.can_analyze(file_path):
        result = html_analyzer.analyze(file_path)
        results.append(result)
    
    return results

def analyze_directory(dir_path: Path, framework_detector: FrameworkDetector, html_analyzer: HTMLAnalyzer) -> List:
    """Analyze all files in a directory"""
    results = []
    
    # Framework detection on directory
    framework_result = framework_detector.analyze(dir_path)
    results.append(framework_result)
    
    # HTML analysis on individual files
    html_files = list(dir_path.rglob("*.html")) + list(dir_path.rglob("*.htm"))
    
    for html_file in html_files[:10]:  # Limit to first 10 files
        if html_analyzer.can_analyze(html_file):
            result = html_analyzer.analyze(html_file)
            results.append(result)
    
    return results

def output_json(results: List, output_file: Optional[Path]):
    """Output results in JSON format"""
    json_data = json.dumps(results, indent=2, default=str)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(json_data)
        click.echo(f"📄 JSON results written to: {output_file}")
    else:
        click.echo(json_data)

def output_summary(results: List, output_file: Optional[Path]):
    """Output results in summary format"""
    summary_lines = []
    summary_lines.append("📊 ANALYSIS SUMMARY")
    summary_lines.append("=" * 50)
    
    for i, result in enumerate(results):
        summary_lines.append(f"\n📁 Result {i+1}:")
        
        if 'frameworks_detected' in result:
            # Framework detection result
            frameworks = result['frameworks_detected']
            summary_lines.append(f"  🎯 Frameworks: {', '.join(frameworks) if frameworks else 'None detected'}")
            summary_lines.append(f"  📁 Files scanned: {result.get('files_scanned', 0)}")
            
        elif 'elements' in result:
            # HTML analysis result
            elements = result['elements']
            summary_lines.append(f"  📄 File: {result.get('file_path', 'Unknown')}")
            summary_lines.append(f"  🏷️  IDs: {len(elements.get('ids', []))}")
            summary_lines.append(f"  🎨 Classes: {len(elements.get('classes', []))}")
            summary_lines.append(f"  📝 Forms: {len(elements.get('forms', []))}")
            summary_lines.append(f"  🔘 Buttons: {len(elements.get('buttons', []))}")
            summary_lines.append(f"  🔗 Links: {len(elements.get('links', []))}")
    
    summary_text = "\n".join(summary_lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(summary_text)
        click.echo(f"📄 Summary written to: {output_file}")
    else:
        click.echo(summary_text)

def display_framework_result(result):
    """Display framework detection result"""
    click.echo(f"\n🎯 Framework Detection:")
    
    frameworks = result.get('frameworks_detected', [])
    if frameworks:
        for framework in frameworks:
            confidence = result.get('confidence', {}).get(framework, 0)
            click.echo(f"  ✅ {framework} (confidence: {confidence})")
    else:
        click.echo("  ❌ No frameworks detected")

def display_html_result(result):
    """Display HTML analysis result"""
    click.echo(f"\n📄 HTML Analysis:")
    
    if 'error' in result:
        click.echo(f"  ❌ Error: {result['error']}")
        return
    
    elements = result.get('elements', {})
    summary = result.get('summary', {})
    
    for key, count in summary.items():
        clean_key = key.replace('total_', '').replace('_', ' ').title()
        click.echo(f"  {clean_key}: {count}")

# Entry point
def main():
    """Main CLI entry point"""
    cli()

if __name__ == '__main__':
    main()
