from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    github_pr_url = fields.Char('GitHub PR URL', help='URL of the related GitHub Pull Request')
