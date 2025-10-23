app_name = "logistay"
app_title = "LogiStay"
app_publisher = "AFMCOltd"
app_description = "LogiStay: Fleet and Accommodation Management"
app_email = "afm@afmcoltd.com"
app_license = "MIT"

# Installation hooks
after_install = "logistay.install.after_install"

# Website route rules
website_route_rules = [
    {"from_route": "/employee-trips-shifts", "to_route": "employee-trips-shifts"},
    {"from_route": "/driver", "to_route": "driver"},
    {"from_route": "/fleet-management", "to_route": "fleet_management"},
    {"from_route": "/booking-lookup", "to_route": "booking-lookup"},
    {"from_route": "/availability", "to_route": "availability"},
    {"from_route": "/supervisor/tasks", "to_route": "supervisor/tasks"},
]

# Fixtures
fixtures = [
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "in", ["Fleet Management", "Accommodation Management"]]
        ]
    },
    {
        "doctype": "Fleet Settings"
    }
]