#!/usr/bin/env python3
"""
Frappe v16 Compliance Audit Script for LogiStay App
Validates DocTypes, Workspaces, and app structure without DB writes
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import re


class FrappeV16Auditor:
    """Comprehensive auditor for Frappe v16 compliance"""
    
    def __init__(self, app_path: str):
        self.app_path = Path(app_path)
        self.app_name = "logistay"
        self.issues = []
        self.doctypes = {}
        self.workspaces = {}
        self.reports = {}
        self.charts = {}
        self.number_cards = {}
        self.modules = set()
        
    def audit_app(self) -> Dict[str, Any]:
        """Run complete audit and return results"""
        print("🔍 Starting Frappe v16 Compliance Audit...")
        
        # Collect all components
        self._collect_doctypes()
        self._collect_workspaces()
        self._collect_reports()
        self._collect_dashboard_components()
        self._collect_modules()
        
        # Validate components
        self._validate_doctypes()
        self._validate_workspaces()
        self._validate_references()
        self._validate_permissions()
        
        # Generate report
        return self._generate_audit_report()
    
    def _collect_doctypes(self):
        """Collect all DocType JSON files"""
        print("📋 Collecting DocTypes...")
        
        doctype_pattern = "**/doctype/*/*.json"
        for json_file in self.app_path.glob(doctype_pattern):
            if json_file.name.endswith('.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if data.get('doctype') == 'DocType':
                        doctype_name = data.get('name', json_file.stem)
                        self.doctypes[doctype_name] = {
                            'path': str(json_file),
                            'data': data,
                            'module': data.get('module', 'Unknown')
                        }
                        self.modules.add(data.get('module', 'Unknown'))
                        
                except Exception as e:
                    self._add_issue('error', f"Failed to parse DocType {json_file}: {e}")
    
    def _collect_workspaces(self):
        """Collect all Workspace JSON files"""
        print("🏢 Collecting Workspaces...")
        
        workspace_pattern = "**/workspace/*.json"
        for json_file in self.app_path.glob(workspace_pattern):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('doctype') == 'Workspace':
                    workspace_name = data.get('name', json_file.stem)
                    self.workspaces[workspace_name] = {
                        'path': str(json_file),
                        'data': data
                    }
                    
            except Exception as e:
                self._add_issue('error', f"Failed to parse Workspace {json_file}: {e}")
    
    def _collect_reports(self):
        """Collect all Report JSON files"""
        print("📊 Collecting Reports...")
        
        report_dir = self.app_path.parent / "report"
        if report_dir.exists():
            for report_folder in report_dir.iterdir():
                if report_folder.is_dir():
                    json_file = report_folder / f"{report_folder.name}.json"
                    if json_file.exists():
                        try:
                            with open(json_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            if data.get('doctype') == 'Report':
                                report_name = data.get('name', report_folder.name)
                                self.reports[report_name] = {
                                    'path': str(json_file),
                                    'data': data
                                }
                                
                        except Exception as e:
                            self._add_issue('error', f"Failed to parse Report {json_file}: {e}")
    
    def _collect_dashboard_components(self):
        """Collect dashboard charts and number cards"""
        print("📈 Collecting Dashboard Components...")
        
        dashboard_dir = self.app_path.parent / "dashboard"
        if dashboard_dir.exists():
            for json_file in dashboard_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract number cards
                    if 'cards' in data:
                        for card in data['cards']:
                            card_name = card.get('card', card.get('label', 'Unknown'))
                            self.number_cards[card_name] = {
                                'path': str(json_file),
                                'data': card
                            }
                    
                    # Extract charts
                    if 'charts' in data:
                        for chart in data['charts']:
                            chart_name = chart.get('chart', chart.get('name', 'Unknown'))
                            self.charts[chart_name] = {
                                'path': str(json_file),
                                'data': chart
                            }
                            
                except Exception as e:
                    self._add_issue('error', f"Failed to parse Dashboard {json_file}: {e}")
    
    def _collect_modules(self):
        """Collect module information"""
        modules_file = self.app_path / "modules.txt"
        if modules_file.exists():
            try:
                with open(modules_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        module = line.strip()
                        if module:
                            self.modules.add(module)
            except Exception as e:
                self._add_issue('error', f"Failed to read modules.txt: {e}")
    
    def _validate_doctypes(self):
        """Validate DocType structure and compliance"""
        print("✅ Validating DocTypes...")
        
        required_fields = ['doctype', 'name', 'module', 'fields']
        
        for doctype_name, doctype_info in self.doctypes.items():
            data = doctype_info['data']
            path = doctype_info['path']
            
            # Check required fields
            for field in required_fields:
                if field not in data:
                    self._add_issue('error', f"DocType {doctype_name} missing required field: {field}", path)
            
            # Validate field structure
            if 'fields' in data:
                fieldnames = set()
                for field in data['fields']:
                    fieldname = field.get('fieldname')
                    if not fieldname:
                        self._add_issue('error', f"DocType {doctype_name} has field without fieldname", path)
                        continue
                    
                    # Check for duplicate fieldnames
                    if fieldname in fieldnames:
                        self._add_issue('error', f"DocType {doctype_name} has duplicate fieldname: {fieldname}", path)
                    fieldnames.add(fieldname)
                    
                    # Validate fieldtype
                    if not field.get('fieldtype'):
                        self._add_issue('error', f"DocType {doctype_name} field {fieldname} missing fieldtype", path)
            
            # Check title_field if specified
            title_field = data.get('title_field')
            if title_field:
                field_exists = any(f.get('fieldname') == title_field for f in data.get('fields', []))
                if not field_exists:
                    self._add_issue('error', f"DocType {doctype_name} title_field '{title_field}' not found in fields", path)
            
            # Validate naming
            autoname = data.get('autoname')
            if autoname and autoname.startswith('field:'):
                field_name = autoname.split(':', 1)[1]
                field_exists = any(f.get('fieldname') == field_name for f in data.get('fields', []))
                if not field_exists:
                    self._add_issue('error', f"DocType {doctype_name} autoname field '{field_name}' not found", path)
    
    def _validate_workspaces(self):
        """Validate Workspace structure and v16 compliance"""
        print("🏢 Validating Workspaces...")
        
        required_fields = ['doctype', 'name', 'title', 'module']
        v16_fields = ['app', 'public', 'icon', 'indicator_color']
        
        for workspace_name, workspace_info in self.workspaces.items():
            data = workspace_info['data']
            path = workspace_info['path']
            
            # Check required fields
            for field in required_fields:
                if field not in data:
                    self._add_issue('error', f"Workspace {workspace_name} missing required field: {field}", path)
            
            # Check v16 recommended fields
            for field in v16_fields:
                if field not in data:
                    self._add_issue('warning', f"Workspace {workspace_name} missing v16 field: {field}", path)
            
            # Validate route
            if 'name' in data:
                route = data['name'].lower().replace(' ', '-')
                if data.get('route') and data['route'] != route:
                    self._add_issue('warning', f"Workspace {workspace_name} route should be '{route}'", path)
            
            # Validate blocks structure
            if 'blocks' in data and not isinstance(data['blocks'], list):
                self._add_issue('error', f"Workspace {workspace_name} blocks must be a list", path)
            
            # Check if workspace is empty
            blocks = data.get('blocks', [])
            links = data.get('links', [])
            shortcuts = data.get('shortcuts', [])
            charts = data.get('charts', [])
            number_cards = data.get('number_cards', [])
            
            if not any([blocks, links, shortcuts, charts, number_cards]):
                self._add_issue('warning', f"Workspace {workspace_name} appears to be empty", path)
    
    def _validate_references(self):
        """Validate references between components"""
        print("🔗 Validating References...")
        
        # Check workspace references to DocTypes, Reports, etc.
        for workspace_name, workspace_info in self.workspaces.items():
            data = workspace_info['data']
            path = workspace_info['path']
            
            # Check links in blocks
            for block in data.get('blocks', []):
                if block.get('block_type') == 'shortcut':
                    link_to = block.get('link_to')
                    link_type = block.get('link_type')
                    
                    if link_type == 'DocType' and link_to:
                        if link_to not in self.doctypes:
                            self._add_issue('error', f"Workspace {workspace_name} references non-existent DocType: {link_to}", path)
                    
                    elif link_type == 'Report' and link_to:
                        if link_to not in self.reports:
                            self._add_issue('error', f"Workspace {workspace_name} references non-existent Report: {link_to}", path)
            
            # Check legacy links array
            for link in data.get('links', []):
                link_to = link.get('link_to')
                link_type = link.get('link_type')
                
                if link_type == 'DocType' and link_to:
                    if link_to not in self.doctypes:
                        self._add_issue('error', f"Workspace {workspace_name} references non-existent DocType: {link_to}", path)
    
    def _validate_permissions(self):
        """Validate permission structure"""
        print("🔐 Validating Permissions...")
        
        for doctype_name, doctype_info in self.doctypes.items():
            data = doctype_info['data']
            path = doctype_info['path']
            
            permissions = data.get('permissions', [])
            if not permissions:
                self._add_issue('warning', f"DocType {doctype_name} has no permissions defined", path)
                continue
            
            # Check for at least one read permission
            has_read = any(perm.get('read') for perm in permissions)
            if not has_read:
                self._add_issue('error', f"DocType {doctype_name} has no read permissions", path)
            
            # Validate role references
            for perm in permissions:
                role = perm.get('role')
                if not role:
                    self._add_issue('error', f"DocType {doctype_name} has permission without role", path)
    
    def _add_issue(self, severity: str, message: str, path: str = ""):
        """Add an issue to the audit results"""
        self.issues.append({
            'severity': severity,
            'message': message,
            'path': path,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def _generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        print("📋 Generating Audit Report...")
        
        # Count issues by severity
        error_count = sum(1 for issue in self.issues if issue['severity'] == 'error')
        warning_count = sum(1 for issue in self.issues if issue['severity'] == 'warning')
        
        # Generate statistics
        stats = {
            'doctypes_found': len(self.doctypes),
            'workspaces_found': len(self.workspaces),
            'reports_found': len(self.reports),
            'charts_found': len(self.charts),
            'number_cards_found': len(self.number_cards),
            'modules_found': len(self.modules),
            'total_issues': len(self.issues),
            'errors': error_count,
            'warnings': warning_count
        }
        
        # Component inventory
        inventory = {
            'doctypes': list(self.doctypes.keys()),
            'workspaces': list(self.workspaces.keys()),
            'reports': list(self.reports.keys()),
            'charts': list(self.charts.keys()),
            'number_cards': list(self.number_cards.keys()),
            'modules': list(self.modules)
        }
        
        return {
            'audit_timestamp': datetime.utcnow().isoformat(),
            'app_name': self.app_name,
            'app_path': str(self.app_path),
            'statistics': stats,
            'inventory': inventory,
            'issues': self.issues,
            'compliance_status': 'PASS' if error_count == 0 else 'FAIL'
        }


def main():
    """Main execution function"""
    if len(sys.argv) != 2:
        print("Usage: python frappe_v16_audit.py <app_path>")
        sys.exit(1)
    
    app_path = sys.argv[1]
    if not os.path.exists(app_path):
        print(f"Error: App path {app_path} does not exist")
        sys.exit(1)
    
    # Run audit
    auditor = FrappeV16Auditor(app_path)
    results = auditor.audit_app()
    
    # Print summary
    print("\n" + "="*60)
    print("📋 FRAPPE V16 COMPLIANCE AUDIT RESULTS")
    print("="*60)
    print(f"App: {results['app_name']}")
    print(f"Audit Time: {results['audit_timestamp']}")
    print(f"Status: {results['compliance_status']}")
    print()
    
    stats = results['statistics']
    print("📊 STATISTICS:")
    print(f"  DocTypes: {stats['doctypes_found']}")
    print(f"  Workspaces: {stats['workspaces_found']}")
    print(f"  Reports: {stats['reports_found']}")
    print(f"  Charts: {stats['charts_found']}")
    print(f"  Number Cards: {stats['number_cards_found']}")
    print(f"  Modules: {stats['modules_found']}")
    print()
    
    print("🚨 ISSUES:")
    print(f"  Errors: {stats['errors']}")
    print(f"  Warnings: {stats['warnings']}")
    print(f"  Total: {stats['total_issues']}")
    print()
    
    # Print issues
    if results['issues']:
        print("📝 DETAILED ISSUES:")
        for issue in results['issues']:
            icon = "❌" if issue['severity'] == 'error' else "⚠️"
            path_info = f" ({issue['path']})" if issue['path'] else ""
            print(f"  {icon} {issue['message']}{path_info}")
    else:
        print("✅ No issues found!")
    
    # Save detailed report
    report_file = f"frappe_v16_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results['compliance_status'] == 'PASS' else 1)


if __name__ == "__main__":
    main()