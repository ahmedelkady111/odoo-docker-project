# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
import os

from odoo import http
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class GithubWebhookController(http.Controller):
    def _verify_signature(self, req):
        """Verify the signature of the GitHub webhook request."""
        secret = os.environ.get('GITHUB_WEBHOOK_SECRET')
        if not secret:
            _logger.error("GITHUB_WEBHOOK_SECRET environment variable not set. Cannot verify webhook signature.")
            # Consider raising a specific configuration error or returning a 500 Internal Server Error
            # For now, denying access is safer.
            raise AccessDenied("Webhook secret not configured.")

        signature_header = req.httprequest.headers.get('X-Hub-Signature-256')
        if not signature_header:
            _logger.warning("Webhook request received without X-Hub-Signature-256 header.")
            raise AccessDenied("Missing signature.")

        # Header format is sha256=<signature_hex>
        sha_name, signature_hex = signature_header.split('=', 1)
        if sha_name != 'sha256':
            _logger.warning("Webhook signature format is not sha256.")
            raise AccessDenied("Unsupported signature format.")

        # Compute the expected signature
        mac = hmac.new(secret.encode('utf-8'), msg=req.httprequest.data, digestmod=hashlib.sha256)
        expected_signature = mac.hexdigest()

        if not hmac.compare_digest(signature_hex, expected_signature):
            _logger.warning("Webhook signature verification failed.")
            raise AccessDenied("Invalid signature.")

        _logger.info("Webhook signature verified successfully.")
        return True # Signature is valid

    @http.route(
        '/github/webhook',
        type='http',
        auth='none',
        methods=['POST'],
        csrf=False,
        save_session=False
    )
    def github_webhook(self, **kw):
        """Handle GitHub webhook to approve project tasks after verifying signature."""
        try:
            self._verify_signature(request)
        except AccessDenied as e:
            _logger.error("Webhook access denied: %s", e)
            return request.make_response(str(e), status=403)

        try:
            payload = json.loads(request.httprequest.data.decode('utf-8'))
        except json.JSONDecodeError:
            _logger.error("Failed to decode JSON payload from webhook.")
            return request.make_response("Invalid JSON payload", status=400)

        _logger.info('Received and verified GitHub webhook payload: %s', payload)

        branch = payload.get('branch')
        user_email = payload.get('user_email')
        task_id_str = payload.get('task_id')

        try:
            task_id = int(task_id_str) if task_id_str else None
        except (ValueError, TypeError):
            _logger.warning("Invalid task_id format received: %s", task_id_str)
            task_id = None

        if branch and user_email and task_id:
            task = request.env['project.task'].sudo().search(
                [('id', '=', task_id)],
                limit=1
            )
            if task:
                approved_stage_id = self._get_approved_stage_id(task)
                if approved_stage_id:
                    try:
                        task.write({'stage_id': approved_stage_id})
                        _logger.info("Task ID %s moved to approved stage. Branch: %s, User: %s", task_id, branch, user_email)
                        # You can also log or store user_email as needed
                        return request.make_json_response({'status': 'success', 'message': 'Task approved'})
                    except Exception as e:
                        _logger.error("Failed to write stage_id for task %s: %s", task_id, e)
                        return request.make_json_response({'status': 'error', 'message': 'Failed to update task stage'}, status=500)
                else:
                    _logger.warning("Could not find an 'Approved' stage for project %s (Task ID: %s).", task.project_id.name, task_id)
                    return request.make_json_response({'status': 'error', 'message': 'Approved stage not found for project'}, status=404)
            else:
                _logger.warning('Task not found for id: %s', task_id)
                return request.make_json_response({'status': 'error', 'message': 'Task not found'}, status=404)
        else:
            _logger.warning('Invalid payload received (missing branch, user_email, or task_id): %s', payload)
            return request.make_json_response({'status': 'error', 'message': 'Invalid payload (missing branch, user_email, or task_id)'}, status=400)

    def _get_approved_stage_id(self, task):
        """Get the configured 'Approved' stage ID for the task's project."""
        if not task.project_id:
            _logger.warning("Task %s has no associated project.", task.id)
            return False

        # Use the configured stage on the project if available
        if task.project_id.approved_stage_id:
            _logger.info("Using configured approved stage ID %s for project %s.", task.project_id.approved_stage_id.id, task.project_id.name)
            return task.project_id.approved_stage_id.id
        else:
            _logger.warning("No 'Approved Stage for Webhook' configured for project '%s' (ID: %s). Task %s cannot be moved automatically.",
                            task.project_id.name, task.project_id.id, task.id)
            # Returning False prevents moving the task if not configured, which is safer.
            # Alternatively, could fall back to the old fragile logic, but explicit configuration is better.
            # Fallback (fragile): 
            # stage = request.env['project.task.type'].sudo().search(
            #     [('name', 'ilike', 'approved'), ('project_ids', 'in', task.project_id.id)], limit=1
            # )
            # return stage.id if stage else False
            return False
