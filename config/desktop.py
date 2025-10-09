from frappe import _

def get_data():
	return [
		{
			"module_name": "Fleet Management",
			"color": "grey",
			"icon": "octicon octicon-package",
			"type": "module",
			"label": _("Fleet Management")
		},
		{
			"module_name": "Accommodation Management",
			"color": "green",
			"icon": "octicon octicon-home",
			"type": "module",
			"label": _("Accommodation Management")
		}
	]