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

## Troubleshooting

*   **Permission Issues**: If you encounter permission errors with Docker, try running with `sudo` or add your user to the `docker` group.
*   **Port Conflicts**: Ensure ports 80 and 8000 are not in use. You can change the host ports in `docker-compose.yml` if necessary.
