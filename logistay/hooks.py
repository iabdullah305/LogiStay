app_name = "logistay"
app_title = "LogiStay"
app_publisher = "AFMCOltd"
app_description = "LogiStay: Fleet and Accommodation Management"
app_email = "afm@afmcoltd.com"
app_license = "MIT"

# Fixtures
fixtures = [
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "in", ["Fleet Management", "Accommodation Management"]]
        ]
    }
]