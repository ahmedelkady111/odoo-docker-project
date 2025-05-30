# __manifest__.py for odoo_project_customize
{
    "name": "Odoo Project Customize",
    "version": "18.0.1.0.0",
    "summary": "Customizations for Odoo Project module",
    "author": "ahmedelkady111",
    "category": "Custom",
    "depends": ["base", "project"],
    "data": [
        "views/project_task_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False
}
