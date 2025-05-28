# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging


_logger = logging.getLogger(__name__)


class GithubWebhookController(http.Controller):
    @http.route(
        '/github/webhook',
        type='json',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def github_webhook(self, **post):
        """Handle GitHub webhook to approve project tasks."""
        _logger.info('Received GitHub webhook: %s', post)
        branch = post.get('branch')
        task_id = post.get('task_id')
        if branch and task_id:
            # Find the task and set its state to 'approved'
            task = request.env['project.task'].sudo().search(
                [('id', '=', task_id)],
                limit=1
            )
            if task:
                task.write({'stage_id': self._get_approved_stage_id(task)})
                return {'status': 'success', 'message': 'Task approved'}
        return {'status': 'error', 'message': 'Invalid payload'}

    def _get_approved_stage_id(self, task):
        """Find the 'Approved' stage for the task's project."""
        stage = request.env['project.task.type'].sudo().search(
            [
                ('name', 'ilike', 'approved'),
                ('project_ids', 'in', task.project_id.id)
            ],
            limit=1
        )
        return stage.id if stage else False
