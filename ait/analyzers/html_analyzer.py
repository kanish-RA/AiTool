"""HTML content analyzer for extracting testable elements"""

import re
from pathlib import Path
from typing import Dict, List, Any, Set
from ..core.base import BaseAnalyzer

class HTMLAnalyzer(BaseAnalyzer):
    """Analyzes HTML files to extract testable elements"""
    
    def __init__(self, name: str = "HTMLAnalyzer"):
        super().__init__(name)
        
        # Common input types for form testing
        self.input_types = [
            'text', 'email', 'password', 'number', 'tel', 'url', 
            'search', 'date', 'time', 'datetime-local', 'month', 
            'week', 'color', 'range', 'file', 'hidden', 'checkbox', 
            'radio', 'submit', 'button', 'reset'
        ]
    
    def can_analyze(self, file_path: Path) -> bool:
        """Can analyze HTML files"""
        return file_path.suffix.lower() in ['.html', '.htm']
    
    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Extract all testable elements from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            elements = {
                'ids': self._extract_ids(content),
                'classes': self._extract_classes(content),
                'names': self._extract_names(content),
                'data_attributes': self._extract_data_attributes(content),
                'forms': self._extract_forms(content),
                'inputs': self._extract_inputs(content),
                'buttons': self._extract_buttons(content),
                'links': self._extract_links(content),
                'headings': self._extract_headings(content),
                'images': self._extract_images(content),
                'tables': self._extract_tables(content),
                'xpaths': []  # Will be generated based on other elements
            }
            
            # Generate XPath expressions based on found elements
            elements['xpaths'] = self._generate_xpaths(elements)
            
            return {
                'file_path': str(file_path),
                'framework': 'HTML',
                'elements': elements,
                'summary': self._generate_summary(elements)
            }
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'framework': 'HTML',
                'error': str(e),
                'elements': {},
                'summary': {}
            }
    
    def _extract_ids(self, content: str) -> List[str]:
        """Extract all id attributes"""
        pattern = r'id\s*=\s*["\']([^"\']+)["\']'
        ids = re.findall(pattern, content, re.IGNORECASE)
        return list(set(ids))  # Remove duplicates
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract all class attributes"""
        pattern = r'class\s*=\s*["\']([^"\']+)["\']'
        class_matches = re.findall(pattern, content, re.IGNORECASE)
        
        # Split multiple classes and flatten
        all_classes = []
        for class_string in class_matches:
            all_classes.extend(class_string.split())
        
        return list(set(all_classes))  # Remove duplicates
    
    def _extract_names(self, content: str) -> List[str]:
        """Extract all name attributes"""
        pattern = r'name\s*=\s*["\']([^"\']+)["\']'
        names = re.findall(pattern, content, re.IGNORECASE)
        return list(set(names))
    
    def _extract_data_attributes(self, content: str) -> List[Dict[str, str]]:
        """Extract data-* attributes"""
        pattern = r'(data-[\w-]+)\s*=\s*["\']([^"\']*)["\']'
        data_attrs = re.findall(pattern, content, re.IGNORECASE)
        
        # Convert to list of dictionaries
        data_list = []
        for attr_name, attr_value in data_attrs:
            data_list.append({
                'attribute': attr_name,
                'value': attr_value
            })
        
        return data_list
    
    def _extract_forms(self, content: str) -> List[Dict[str, Any]]:
        """Extract form elements and their attributes"""
        forms = []
        
        # Find all form tags
        form_pattern = r'<form([^>]*)>(.*?)</form>'
        form_matches = re.findall(form_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (form_attrs, form_content) in enumerate(form_matches):
            form_info = {
                'form_id': f"form_{i}",
                'action': self._extract_attribute(form_attrs, 'action'),
                'method': self._extract_attribute(form_attrs, 'method') or 'GET',
                'inputs': self._extract_inputs(form_content),
                'buttons': self._extract_buttons(form_content)
            }
            forms.append(form_info)
        
        return forms
    
    def _extract_inputs(self, content: str) -> List[Dict[str, str]]:
        """Extract input elements"""
        inputs = []
        
        # Pattern to match input tags
        input_pattern = r'<input([^>]*)/?>'
        input_matches = re.findall(input_pattern, content, re.IGNORECASE)
        
        for input_attrs in input_matches:
            input_info = {
                'type': self._extract_attribute(input_attrs, 'type') or 'text',
                'name': self._extract_attribute(input_attrs, 'name'),
                'id': self._extract_attribute(input_attrs, 'id'),
                'placeholder': self._extract_attribute(input_attrs, 'placeholder'),
                'value': self._extract_attribute(input_attrs, 'value'),
                'required': 'required' in input_attrs.lower()
            }
            inputs.append(input_info)
        
        return inputs
    
    def _extract_buttons(self, content: str) -> List[Dict[str, str]]:
        """Extract button elements"""
        buttons = []
        
        # Button tags
        button_pattern = r'<button([^>]*)>(.*?)</button>'
        button_matches = re.findall(button_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for button_attrs, button_text in button_matches:
            button_info = {
                'type': self._extract_attribute(button_attrs, 'type') or 'button',
                'text': re.sub(r'<[^>]+>', '', button_text).strip(),
                'id': self._extract_attribute(button_attrs, 'id'),
                'class': self._extract_attribute(button_attrs, 'class')
            }
            buttons.append(button_info)
        
        # Input buttons
        input_button_pattern = r'<input([^>]*type\s*=\s*["\'](?:button|submit|reset)["\'][^>]*)/?>'
        input_button_matches = re.findall(input_button_pattern, content, re.IGNORECASE)
        
        for button_attrs in input_button_matches:
            button_info = {
                'type': self._extract_attribute(button_attrs, 'type'),
                'text': self._extract_attribute(button_attrs, 'value'),
                'id': self._extract_attribute(button_attrs, 'id'),
                'class': self._extract_attribute(button_attrs, 'class')
            }
            buttons.append(button_info)
        
        return buttons
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract link elements"""
        links = []
        
        link_pattern = r'<a([^>]*)>(.*?)</a>'
        link_matches = re.findall(link_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for link_attrs, link_text in link_matches:
            link_info = {
                'href': self._extract_attribute(link_attrs, 'href'),
                'text': re.sub(r'<[^>]+>', '', link_text).strip(),
                'id': self._extract_attribute(link_attrs, 'id'),
                'class': self._extract_attribute(link_attrs, 'class'),
                'target': self._extract_attribute(link_attrs, 'target')
            }
            links.append(link_info)
        
        return links
    
    def _extract_headings(self, content: str) -> List[Dict[str, str]]:
        """Extract heading elements (h1-h6)"""
        headings = []
        
        for level in range(1, 7):
            pattern = f'<h{level}([^>]*)>(.*?)</h{level}>'
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            
            for heading_attrs, heading_text in matches:
                heading_info = {
                    'level': f'h{level}',
                    'text': re.sub(r'<[^>]+>', '', heading_text).strip(),
                    'id': self._extract_attribute(heading_attrs, 'id'),
                    'class': self._extract_attribute(heading_attrs, 'class')
                }
                headings.append(heading_info)
        
        return headings
    
    def _extract_images(self, content: str) -> List[Dict[str, str]]:
        """Extract image elements"""
        images = []
        
        img_pattern = r'<img([^>]*)/?>'
        img_matches = re.findall(img_pattern, content, re.IGNORECASE)
        
        for img_attrs in img_matches:
            img_info = {
                'src': self._extract_attribute(img_attrs, 'src'),
                'alt': self._extract_attribute(img_attrs, 'alt'),
                'id': self._extract_attribute(img_attrs, 'id'),
                'class': self._extract_attribute(img_attrs, 'class')
            }
            images.append(img_info)
        
        return images
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract table elements"""
        tables = []
        
        table_pattern = r'<table([^>]*)>(.*?)</table>'
        table_matches = re.findall(table_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for i, (table_attrs, table_content) in enumerate(table_matches):
            # Count rows and headers
            rows = len(re.findall(r'<tr[^>]*>', table_content, re.IGNORECASE))
            headers = len(re.findall(r'<th[^>]*>', table_content, re.IGNORECASE))
            
            table_info = {
                'table_id': f"table_{i}",
                'id': self._extract_attribute(table_attrs, 'id'),
                'class': self._extract_attribute(table_attrs, 'class'),
                'rows': rows,
                'headers': headers
            }
            tables.append(table_info)
        
        return tables
    
    def _extract_attribute(self, attrs_string: str, attr_name: str) -> str:
        """Extract specific attribute value from attributes string"""
        pattern = f'{attr_name}\\s*=\\s*["\']([^"\']*)["\']'
        match = re.search(pattern, attrs_string, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _generate_xpaths(self, elements: Dict[str, Any]) -> List[str]:
        """Generate useful XPath expressions based on found elements"""
        xpaths = []
        
        # XPaths for IDs
        for id_val in elements['ids'][:5]:  # Limit to first 5
            xpaths.append(f"//*[@id='{id_val}']")
        
        # XPaths for classes
        for class_val in elements['classes'][:5]:
            xpaths.append(f"//*[@class='{class_val}']")
        
        # XPaths for form elements
        if elements['forms']:
            xpaths.extend([
                "//form",
                "//input[@type='submit']",
                "//input[@type='button']",
                "//button[@type='submit']"
            ])
        
        # XPaths for common elements
        xpaths.extend([
            "//a[contains(@href, 'login')]",
            "//a[contains(@href, 'logout')]",
            "//input[@type='email']",
            "//input[@type='password']",
            "//div[contains(@class, 'error')]",
            "//div[contains(@class, 'success')]",
            "//h1 | //h2 | //h3",
            "//table//tr",
            "//img[@alt]"
        ])
        
        return xpaths
    
    def _generate_summary(self, elements: Dict[str, Any]) -> Dict[str, int]:
        """Generate summary statistics"""
        return {
            'total_ids': len(elements['ids']),
            'total_classes': len(elements['classes']),
            'total_names': len(elements['names']),
            'total_forms': len(elements['forms']),
            'total_inputs': len(elements['inputs']),
            'total_buttons': len(elements['buttons']),
            'total_links': len(elements['links']),
            'total_headings': len(elements['headings']),
            'total_images': len(elements['images']),
            'total_tables': len(elements['tables']),
            'total_data_attributes': len(elements['data_attributes'])
        }