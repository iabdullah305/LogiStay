import os, frappe, subprocess, json, inspect

def run_cmd(cmd): 
    subprocess.run(cmd, shell=True, check=False)

def diagnose(site):
    print("=== Apps ===")
    run_cmd(f"bench --site {site} list-apps")
    
    print("\n=== Workspaces ===")
    print(frappe.get_all("Workspace", pluck="name"))
    
    print("\n=== Route Conflicts ===")
    print(frappe.get_all("Page", pluck="name"))
    
    print("\n=== Meta Fields ===")
    meta = frappe.get_meta('Workspace')
    print("Workspace fields:", meta.get_fieldnames())
    print("Has content field:", "content" in meta.get_fieldnames())
    
    print("\n=== Legacy Model Detection ===")
    from frappe.desk.doctype.workspace.workspace import Workspace
    source = inspect.getsource(Workspace.validate)
    print("Legacy validator (loads content):", "loads(self.content)" in source)
    
    print("\n=== Module Check ===")
    print("Fleet Management module exists:", frappe.db.exists("Module Def", "Fleet Management"))
    
    print("\n=== Current User Roles ===")
    print("Roles:", frappe.get_roles())
    
    print("\n=== Workspace DB Record ===")
    print("fleet_management exists in DB:", frappe.db.exists("Workspace", "fleet_management"))
    print("Fleet Management exists in DB:", frappe.db.exists("Workspace", "Fleet Management"))
    
    print("\n=== Page Conflicts ===")
    conflicts = frappe.get_all("Page", filters={"name": ["in", ["fleet-management", "Fleet Management"]]}, pluck="name")
    print("Page conflicts:", conflicts)