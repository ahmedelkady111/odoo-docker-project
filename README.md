# Odoo 18 Docker Project with GitHub Webhook Integration

This project provides a setup for running an Odoo 18 instance using Docker and Docker Compose. It includes a custom Odoo module (`odoo_project_customize`) that adds a GitHub Pull Request URL field to project tasks and features a secure webhook endpoint to automatically move tasks to a designated 'Approved' stage based on GitHub events.

## Features

-   Dockerized Odoo 18 environment.
-   PostgreSQL database service.
-   Secure credential management using environment variables (`.env` file).
-   Custom Odoo module (`odoo_project_customize`):
    -   Adds a `github_pr_url` field to `project.task`.
    -   Adds a configurable `approved_stage_id` field to `project.project`.
    -   Provides a secure `/github/webhook` endpoint.
-   Webhook security implemented using GitHub signature verification (HMAC-SHA256).
-   Correct Docker volume configuration for custom addons and persistent data.
-   Standardized logging to stdout/stderr.

## Project Structure

```
.
├── Dockerfile              # Builds the custom Odoo image
├── docker-compose.yml      # Defines Docker services (Odoo, PostgreSQL)
├── config/
│   └── odoo.conf           # Odoo server configuration file
├── addons/
│   └── odoo_project_customize/ # Custom Odoo module source code
│       ├── __init__.py
│       ├── __manifest__.py
│       ├── controllers/
│       │   ├── __init__.py
│       │   └── main.py       # Contains the webhook controller logic
│       ├── models/
│       │   ├── __init__.py
│       │   ├── project_project.py # Adds approved_stage_id field
│       │   └── project_task.py    # Adds github_pr_url field
│       └── views/
│           └── project_task_views.xml # Adds fields to the task form view
├── .env.example            # Example environment variables file
└── README.md               # This file
```

## Getting Started

### Prerequisites

-   Docker Engine
-   Docker Compose

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ahmedelkady111/odoo-docker-project.git # Or your fork
    cd odoo-docker-project
    ```

2.  **Create the environment file:**
    Copy the example environment file to `.env`:
    ```bash
    cp .env.example .env
    ```
    **Edit the `.env` file** and set secure values for the following variables:
    -   `POSTGRES_PASSWORD`: Choose a strong password for the PostgreSQL database user.
    -   `GITHUB_WEBHOOK_SECRET`: Generate a strong, random secret string for verifying GitHub webhook requests. You can use a password generator or a command like `openssl rand -hex 32`.
    -   Optionally adjust `ODOO_PORT`, `POSTGRES_USER`, `POSTGRES_DB` if needed.

3.  **Build and start the containers:**
    ```bash
    docker-compose up --build -d
    ```
    The `--build` flag ensures the Odoo image is built with any changes. The `-d` flag runs the containers in detached mode.

4.  **Access Odoo:**
    Open your web browser and navigate to `http://localhost:${ODOO_PORT}` (e.g., `http://localhost:8069` if using the default port).
    You will be prompted to create a new Odoo database. Use the PostgreSQL credentials defined in your `.env` file if needed, although Odoo should pick them up automatically.

5.  **Install the Custom Module:**
    -   Log in to Odoo.
    -   Go to `Apps`.
    -   Click `Update Apps List` (you might need to activate developer mode first: Settings -> Activate the developer mode).
    -   Remove the default `Apps` filter.
    -   Search for `Odoo Project Customize`.
    -   Click `Install`.

### Configuring the GitHub Webhook

To enable the automatic task approval feature:

1.  **Configure the Approved Stage in Odoo:**
    -   Navigate to the `Project` application.
    -   Go to `Configuration` -> `Projects`.
    -   Select the project you want to integrate with the webhook.
    -   Click `Edit`.
    -   In the `Approved Stage for Webhook` field, select the specific stage (e.g., "Approved", "Done") that tasks should be moved to when the webhook is triggered successfully.
    -   Click `Save`.
    *Note: If this field is not set for a project, the webhook will not move tasks within that project.* 

2.  **Set up the Webhook in GitHub:**
    -   Go to the settings page of the GitHub repository you want to send webhooks from.
    -   Navigate to `Webhooks`.
    -   Click `Add webhook`.
    -   **Payload URL**: Enter the public URL of your Odoo instance followed by `/github/webhook`. For local testing, you might need a tool like `ngrok` to expose your local Odoo instance to the internet (e.g., `https://<your-ngrok-id>.ngrok.io/github/webhook`).
    -   **Content type**: Select `application/json`.
    -   **Secret**: Enter the **exact same secret** you defined in the `GITHUB_WEBHOOK_SECRET` variable in your `.env` file.
    -   **Which events would you like to trigger this webhook?**: Choose the events relevant to your workflow (e.g., `Pull request reviews`, `Pushes`, etc.). The current implementation expects a JSON payload containing `branch` and `task_id` keys.
    -   Ensure the webhook is `Active`.
    -   Click `Add webhook`.

### Usage

-   The custom module adds a `GitHub PR URL` field to the Project Task form.
-   When a correctly configured and verified GitHub webhook request containing a valid `task_id` is received at `/github/webhook`, the corresponding task will be moved to the stage configured in the `Approved Stage for Webhook` field of its project.
-   Check the Odoo server logs for details on received webhooks and signature verification status.

### Stopping the Environment

To stop the containers:
```bash
docker-compose down
```
To stop and remove the data volumes (use with caution!):
```bash
docker-compose down -v
```

## Development Notes

-   The Odoo container uses the `odoo:18` base image (consider pinning to a specific minor version like `odoo:18.0` for stability).
-   Custom addons are mounted from the local `./addons` directory into `/mnt/extra-addons` inside the container.
-   Odoo logs are configured to output to stdout/stderr for easy collection via `docker logs` or standard Docker logging drivers.
-   Database credentials and the webhook secret are managed securely via the `.env` file.
-   The PostgreSQL port is not exposed externally by default for better security.

