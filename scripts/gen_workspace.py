import os
import json
import argparse
from datetime import datetime

def get_doctypes(app_path):
    doctypes = []
    doctype_path = os.path.join(app_path, 'logistay', 'doctype')
    for doctype in os.listdir(doctype_path):
        if os.path.isdir(os.path.join(doctype_path, doctype)):
            doctypes.append(doctype.replace('_', ' ').title())
    return doctypes

def get_reports(app_path):
    reports = []
    report_path = os.path.join(app_path, 'logistay', 'report')
    for report in os.listdir(report_path):
        if os.path.isdir(os.path.join(report_path, report)):
            reports.append(report.replace('_', ' ').title())
    return reports

def generate_workspace(app, module, workspace_name, out_path):
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    doctypes = get_doctypes(app_path)
    reports = get_reports(app_path)

    workspace = {
        "doctype": "Workspace",
        "name": workspace_name,
        "title": workspace_name,
        "module": module,
        "public": 1,
        "is_hidden": 0,
        "is_standard": 1,
        "icon": "folder-open",
        "sequence_id": 1,
        "creation": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
        "modified": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
        "generated_at": datetime.utcnow().isoformat(),
        "blocks": [
            {
                "type": "shortcut",
                "label": "DocTypes",
                "links": [{"type": "DocType", "label": doc, "name": doc} for doc in doctypes]
            },
            {
                "type": "report",
                "label": "Reports",
                "reports": [{"name": report} for report in reports]
            }
        ]
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(workspace, f, indent=2)

    print(f"Workspace generated at {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a complete, rich workspace for Frappe v16.")
    parser.add_argument("--app", required=True, help="The name of the app.")
    parser.add_argument("--module", required=True, help="The name of the module.")
    parser.add_argument("--workspace", required=True, help="The name of the workspace.")
    parser.add_argument("--out", required=True, help="The output path for the workspace JSON file.")
    args = parser.parse_args()

    generate_workspace(args.app, args.module, args.workspace, args.out)