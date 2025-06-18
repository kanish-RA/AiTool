"""AI-Enhanced Gherkin BDD scenario generator"""

from typing import Dict, List, Any, Set, Optional
from datetime import datetime
from ..core.base import BaseGenerator
from ..ai.ollama_provider import OllamaProvider

class GherkinGenerator(BaseGenerator):
    """Generates Gherkin BDD scenarios from analysis results using AI when available"""
    
    def __init__(self, name: str = "GherkinGenerator", ai_provider: Optional[OllamaProvider] = None):
        super().__init__(name)
        
        # Initialize AI provider
        self.ai_provider = ai_provider or OllamaProvider()
        self.ai_enabled = self.ai_provider.is_available()
        
        if self.ai_enabled:
            print(f"🤖 AI-enhanced Gherkin generation enabled")
        else:
            print(f"📝 Using rule-based Gherkin generation (AI not available)")
        
        # Fallback scenario templates (same as before)
        self.scenario_templates = {
            'login_form': {
                'title': 'User Login with Valid Credentials',
                'tags': ['@smoke', '@authentication'],
                'description': 'Test user authentication with valid credentials'
            },
            'form_submission': {
                'title': 'Form Submission with Valid Data',
                'tags': ['@form', '@validation'],
                'description': 'Test form submission with valid input data'
            },
            'navigation': {
                'title': 'Navigation Through Application',
                'tags': ['@navigation', '@ui'],
                'description': 'Test navigation between different pages'
            }
        }
    
    def can_generate(self, analysis_results: List[Dict[str, Any]]) -> bool:
        """Can generate Gherkin for any analysis results"""
        return len(analysis_results) > 0
    
    def generate(self, analysis_results: List[Dict[str, Any]], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate Gherkin scenarios using AI when available, fallback to rule-based"""
        options = options or {}
        
        # Combine analysis results
        combined_analysis = self._combine_analysis_results(analysis_results)
        
        # Try AI generation first
        if self.ai_enabled and options.get('use_ai', True):
            print("🤖 Attempting AI-powered Gherkin generation...")
            ai_scenarios = self._generate_with_ai(combined_analysis, options)
            
            if ai_scenarios:
                feature_content = self._build_feature_file_from_ai(ai_scenarios, combined_analysis, options)
                return {
                    'content': feature_content,
                    'format': 'gherkin',
                    'generation_method': 'ai_powered',
                    'scenarios_count': len(ai_scenarios),
                    'analysis_summary': combined_analysis['summary'],
                    'generated_at': datetime.now().isoformat()
                }
        
        # Fallback to rule-based generation
        print("📝 Using rule-based Gherkin generation...")
        scenarios = self._generate_rule_based_scenarios(combined_analysis)
        feature_content = self._build_feature_file(scenarios, combined_analysis, options)
        
        return {
            'content': feature_content,
            'format': 'gherkin',
            'generation_method': 'rule_based',
            'scenarios_count': len(scenarios),
            'analysis_summary': combined_analysis['summary'],
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_with_ai(self, analysis: Dict[str, Any], options: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Generate scenarios using AI"""
        
        # Create detailed prompt for AI
        prompt = self._create_ai_prompt(analysis, options)
        
        # Get AI response
        ai_response = self.ai_provider.generate_text(prompt)
        
        if not ai_response:
            return None
        
        # Parse AI response into scenarios
        try:
            scenarios = self._parse_ai_response(ai_response)
            print(f"✅ AI generated {len(scenarios)} scenarios")
            return scenarios
        except Exception as e:
            print(f"❌ Failed to parse AI response: {e}")
            return None
    
    def _create_ai_prompt(self, analysis: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Create detailed prompt for AI Gherkin generation"""
        
        # Summarize what we found
        elements_summary = []
        all_elements = analysis['all_elements']
        
        if all_elements['forms']:
            elements_summary.append(f"- {len(all_elements['forms'])} form(s) detected")
            if analysis['has_authentication']:
                elements_summary.append("- Authentication/login functionality detected")
        
        if all_elements['buttons']:
            elements_summary.append(f"- {len(all_elements['buttons'])} interactive button(s)")
        
        if all_elements['links']:
            elements_summary.append(f"- {len(all_elements['links'])} navigation link(s)")
        
        if all_elements['tables']:
            elements_summary.append(f"- {len(all_elements['tables'])} data table(s)")
        
        if all_elements['images']:
            elements_summary.append(f"- {len(all_elements['images'])} image(s)")
        
        # Create the AI prompt
        prompt = f"""You are a BDD testing expert. Generate realistic Gherkin scenarios for a web application based on this analysis:

ANALYSIS RESULTS:
{chr(10).join(elements_summary)}

FRAMEWORKS DETECTED: {', '.join(analysis['summary']['frameworks_detected']) or 'HTML/Generic Web'}

FILES ANALYZED: {analysis['summary']['total_files']}

SPECIFIC ELEMENTS FOUND:
- IDs: {', '.join(all_elements['ids'][:10])}
- Button types: {', '.join([btn.get('type', 'button') for btn in all_elements['buttons'][:5]])}
- Form actions: {', '.join([form.get('action', 'unknown') for form in all_elements['forms'][:3]])}

REQUIREMENTS:
1. Generate 6-8 realistic test scenarios
2. Focus on actual functionality found in the analysis
3. Include both positive and negative test cases
4. Use proper Gherkin format (Given/When/Then)
5. Add appropriate tags (@automation, @smoke, @ui, @form, @navigation, etc.)
6. Make scenarios specific to the detected elements

EXAMPLE FORMAT:
@automation @smoke
Scenario: Specific functionality test
  Given I am on the [specific page]
  When I [specific action with detected elements]
  Then I should [expected result]
  And [additional verification]

Generate comprehensive scenarios that would actually test the functionality represented by these HTML elements. Focus on user workflows that make sense for this application.

SCENARIOS:"""

        return prompt
    
    def _parse_ai_response(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured scenarios"""
        scenarios = []
        current_scenario = None
        current_tags = []
        
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Detect tags
            if line.startswith('@'):
                current_tags = line.split()
                continue
            
            # Detect scenario start
            if line.startswith('Scenario:'):
                # Save previous scenario
                if current_scenario:
                    scenarios.append(current_scenario)
                
                # Start new scenario
                title = line.replace('Scenario:', '').strip()
                current_scenario = {
                    'title': title,
                    'tags': current_tags.copy(),
                    'steps': []
                }
                current_tags = []
                continue
            
            # Detect steps (Given/When/Then/And/But)
            if any(line.startswith(keyword) for keyword in ['Given', 'When', 'Then', 'And', 'But']):
                if current_scenario:
                    current_scenario['steps'].append(line)
                continue
        
        # Don't forget the last scenario
        if current_scenario:
            scenarios.append(current_scenario)
        
        return scenarios
    
    def _build_feature_file_from_ai(self, scenarios: List[Dict[str, Any]], analysis: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Build feature file from AI-generated scenarios"""
        
        # Determine feature name
        frameworks = analysis['summary']['frameworks_detected']
        if frameworks:
            feature_name = f"{', '.join(frameworks)} Application Testing"
        else:
            feature_name = "Web Application Testing"
        
        lines = []
        
        # Feature header
        lines.append(f"Feature: {feature_name}")
        lines.append("  As a quality assurance engineer")
        lines.append("  I want to test all aspects of the web application")
        lines.append("  So that I can ensure quality and reliability")
        lines.append("")
        
        # Background
        lines.append("  Background:")
        lines.append("    Given the web application is running and accessible")
        lines.append("    And I have a clean browser session")
        lines.append("")
        
        # Add AI-generated scenarios
        for scenario in scenarios:
            # Tags
            if scenario.get('tags'):
                lines.append(f"  {' '.join(scenario['tags'])}")
            
            # Scenario title
            lines.append(f"  Scenario: {scenario['title']}")
            
            # Steps
            for step in scenario['steps']:
                lines.append(f"    {step}")
            
            lines.append("")
        
        # Metadata
        lines.append("# Generated by AI Testing Framework using AI")
        lines.append(f"# AI Model: {self.ai_provider.model}")
        lines.append(f"# Analysis Summary:")
        lines.append(f"#   Files analyzed: {analysis['summary']['total_files']}")
        lines.append(f"#   Forms found: {analysis['summary']['total_forms']}")
        lines.append(f"#   Authentication flow: {analysis['summary']['has_authentication_flow']}")
        lines.append(f"#   Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)
    
    def _combine_analysis_results(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple analysis results (same as before)"""
        combined = {
            'frameworks': set(),
            'all_elements': {
                'ids': [],
                'classes': [],
                'forms': [],
                'inputs': [],
                'buttons': [],
                'links': [],
                'headings': [],
                'images': [],
                'tables': []
            },
            'has_forms': False,
            'has_navigation': False,
            'has_authentication': False,
            'files_analyzed': []
        }
        
        for result in analysis_results:
            if 'framework' in result:
                combined['frameworks'].add(result['framework'])
            
            if 'file_path' in result:
                combined['files_analyzed'].append(result['file_path'])
            
            if 'elements' in result:
                elements = result['elements']
                
                for key in ['ids', 'classes', 'forms', 'inputs', 'buttons', 'links', 'headings', 'images', 'tables']:
                    if key in elements:
                        combined['all_elements'][key].extend(elements[key])
                
                if elements.get('forms'):
                    combined['has_forms'] = True
                
                if elements.get('links'):
                    combined['has_navigation'] = True
                
                # Check for authentication
                auth_indicators = ['login', 'password', 'username', 'email', 'signin', 'auth']
                for form in elements.get('forms', []):
                    for input_field in form.get('inputs', []):
                        if any(indicator in str(input_field).lower() for indicator in auth_indicators):
                            combined['has_authentication'] = True
                            break
        
        # Remove duplicates
        for key in combined['all_elements']:
            if isinstance(combined['all_elements'][key], list) and key in ['ids', 'classes']:
                combined['all_elements'][key] = list(set(combined['all_elements'][key]))
        
        combined['summary'] = {
            'frameworks_detected': list(combined['frameworks']),
            'total_files': len(combined['files_analyzed']),
            'total_forms': len(combined['all_elements']['forms']),
            'total_buttons': len(combined['all_elements']['buttons']),
            'total_links': len(combined['all_elements']['links']),
            'has_authentication_flow': combined['has_authentication']
        }
        
        return combined
    
    def _generate_rule_based_scenarios(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate scenarios using rule-based approach (fallback)"""
        scenarios = []
        
        # Same rule-based logic as before...
        if analysis['has_authentication']:
            scenarios.append({
                'title': 'User Authentication with Valid Credentials',
                'tags': ['@smoke', '@authentication', '@automation'],
                'steps': [
                    'Given I am on the login page',
                    'When I enter valid username and password',
                    'And I click the login button',
                    'Then I should be redirected to the dashboard',
                    'And I should see a welcome message'
                ]
            })
        
        # Add more rule-based scenarios...
        scenarios.append({
            'title': 'Page Load and Basic Functionality',
            'tags': ['@smoke', '@ui', '@automation'],
            'steps': [
                'Given I navigate to the application',
                'When the page loads completely',
                'Then all elements should be displayed correctly',
                'And there should be no JavaScript errors'
            ]
        })
        
        return scenarios
    
    def _build_feature_file(self, scenarios: List[Dict[str, Any]], analysis: Dict[str, Any], options: Dict[str, Any]) -> str:
        """Build feature file from rule-based scenarios (same as before)"""
        frameworks = analysis['summary']['frameworks_detected']
        feature_name = f"{', '.join(frameworks)} Application Testing" if frameworks else "Web Application Testing"
        
        lines = []
        lines.append(f"Feature: {feature_name}")
        lines.append("  As a quality assurance engineer")
        lines.append("  I want to test all aspects of the web application")
        lines.append("  So that I can ensure quality and reliability")
        lines.append("")
        
        lines.append("  Background:")
        lines.append("    Given the web application is running and accessible")
        lines.append("    And I have a clean browser session")
        lines.append("")
        
        for scenario in scenarios:
            if scenario.get('tags'):
                lines.append(f"  {' '.join(scenario['tags'])}")
            lines.append(f"  Scenario: {scenario['title']}")
            for step in scenario['steps']:
                lines.append(f"    {step}")
            lines.append("")
        
        lines.append("# Generated by AI Testing Framework (rule-based)")
        lines.append(f"# Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)