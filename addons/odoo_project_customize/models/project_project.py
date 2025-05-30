from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    approved_stage_id = fields.Many2one(
        'project.task.type',
        string='Approved Stage for Webhook',
        help="The specific stage to move tasks to when approved via the GitHub webhook.",
        domain="[('project_ids', '=', id)]" # Ensure stage belongs to this project
    )

