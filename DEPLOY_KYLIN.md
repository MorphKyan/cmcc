# Deployment Guide for Kylin V10

This guide describes how to deploy the application on a Kylin V10 server using Docker.

## Prerequisites

1.  **Docker & Docker Compose**: Ensure Docker is installed.
    *   Kylin V10 is based on Linux. You can usually install Docker using the standard installation script or package manager.
    *   Verify installation: `docker --version` and `docker compose version`.

## Project Structure Setup

Ensure the project files are on the server. You can transfer them via `scp`, `git clone`, or USB.

Required files/directories:
*   `Dockerfile.backend`
*   `Dockerfile.frontend`
*   `docker-compose.yml`
*   `requirements.txt`
*   `main.py`
*   `src/`
*   `frontend/` (containing Vue source and `nginx.conf`)
*   `config/`
*   `data/`

## Deployment Steps

1.  **Navigate to the project directory**:
    ```bash
    cd /path/to/cmcc
    ```

2.  **Build and Start Services**:
    Run the following command to build the images and start the containers in the background.
    ```bash
    docker compose up -d --build
    ```

3.  **Verify Deployment**:
    *   Check running containers:
        ```bash
        docker compose ps
        ```
    *   View logs if needed:
        ```bash
        docker compose logs -f
        ```

4.  **Access the Application**:
    *   Frontend: `https://<server-ip>` (HTTP will redirect to HTTPS)
    *   Backend API: `https://<server-ip>/api` (proxied via Nginx)

## Maintenance

*   **Stop Services**:
    ```bash
    docker compose down
    ```
*   **Restart Services**:
    ```bash
    docker compose restart
    ```
*   **Update Application**:
    1.  Pull new code (e.g., `git pull`).
    2.  Rebuild and restart:
        ```bash
        docker compose up -d --build
        ```

## Logs Management

Application logs are persisted to the host filesystem for debugging and monitoring.

*   **Backend Logs**: Located in `./logs/` directory
    *   Main application logs: `./logs/app_YYYY-MM-DD.log` (rotated daily)
    *   Error logs: `./logs/error_YYYY-MM-DD.log` (ERROR level and above)
    *   View today's logs: `tail -f logs/app_$(date +%Y-%m-%d).log`
    *   View error logs: `tail -f logs/error_$(date +%Y-%m-%d).log`
    *   Logs are automatically compressed after rotation (`.zip` files)
    *   Retention: 30 days for main logs, 60 days for error logs
    
*   **Nginx Access/Error Logs**: Located in `./logs/nginx/`
    *   Access log: `./logs/nginx/access.log`
    *   Error log: `./logs/nginx/error.log`
    *   View real-time access logs: `tail -f logs/nginx/access.log`
    
*   **Container Logs** (Docker logs):
    *   View backend logs: `docker compose logs -f backend`
    *   View frontend logs: `docker compose logs -f frontend`
    *   View all logs: `docker compose logs -f`

**Log Rotation**: Consider setting up log rotation to prevent logs from consuming too much disk space. You can use `logrotate` on the host system.

## Troubleshooting

*   **Permission Issues**: If you encounter permission errors with Docker, try running with `sudo` or add your user to the `docker` group.
*   **Port Conflicts**: Ensure ports 80 and 8000 are not in use. You can change the host ports in `docker-compose.yml` if necessary.
*   **Log Files Not Created**: Ensure the `logs/` and `logs/nginx/` directories exist and have proper permissions. Docker will create them automatically if the parent directory is writable.
