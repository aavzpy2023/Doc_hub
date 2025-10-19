# Doc_hub: A Self-Hosted, Version-Controlled Documentation Platform

![Python](https://img.shields.io/badge/Python-3.11-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green.svg) ![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-lightgrey.svg)

Doc_hub is a comprehensive web platform for creating, managing, and publishing technical documentation using Markdown. The application is built on a modern tech stack (FastAPI, PostgreSQL, Nginx), follows a professional modular architecture, and is fully containerized with Docker. It provides a robust system for automatic version control of every change using Git.

## Core Features

* **Web-Based Markdown Editor:** A rich user interface for writing and previewing Markdown documents (powered by EasyMDE).
* **Automatic Git Versioning:** Every document save triggers a Git commit, providing a complete and auditable change history.
* **User Authentication:** Secure login system based on JWT (OAuth2) with user and admin roles.
* **Static Site Generation:** Administrators can build and publish a navigable static documentation website using **MkDocs** with a single click.
* **PDF Export:** Generate high-quality PDFs from any Markdown document on the fly using **Pandoc**.
* **Robust & Scalable Architecture:** Deployed with Docker Compose, using Nginx as a reverse proxy and following a clean, service-oriented structure.

## The Problem It Solves

Development and QA teams need a "single source of truth" for their documentation (user manuals, API guides, testing procedures). Doc_hub centralizes this process, ensuring all documentation is organized, easy to edit, and version-controlled, thus eliminating the chaos of scattered files and outdated versions.

## Technology Architecture

The system follows a modular, service-oriented architecture orchestrated by Docker Compose. Each component is encapsulated in its own directory, reflecting a clean separation of concerns:

1. **`/proxy` (Nginx Reverse Proxy):** The single entry point for all traffic. It intelligently routes requests to the backend API and efficiently serves the generated static documentation site.
2. **`/backend` (FastAPI Application):** The application's brain. This service contains all the business logic, API endpoints (`/api`), user authentication, Git interactions, and document generation tasks (PDF/Website).
3. **Database (PostgreSQL):** A dedicated PostgreSQL container that stores persistent data such as users, document locks, and comments.

---

## Project Status & Roadmap

This project is currently **under active development**. The core functionalities are implemented and operational.

### Current Status

* [x] User Authentication & Authorization (JWT-based).

* [x] Web-based Markdown Editor with live preview.
* [x] Automatic Git versioning on every save.
* [x] Static site generation with MkDocs.
* [x] On-the-fly PDF export with Pandoc.
* [x] Fully containerized with a professional modular architecture.

### Future Roadmap

* **[ ] Document Locking:** Implement a real-time locking system to prevent simultaneous edits.

* **[ ] Commenting System:** Develop a commenting feature per document for collaborative review.
* **[ ] Full-Text Search:** Integrate a search engine (e.g., Elasticsearch) for powerful searching across all documents.
* **[ ] CI/CD Pipeline:** Create a GitHub Actions workflow to automate testing and deployment.
* **[ ] Enhanced Permissions:** Develop a more granular permission system (e.g., read/write per directory).

---

## Getting Started

### Prerequisites

* Docker
* Docker Compose

### Installation & Launch

1. **Clone the Repository:**

    ```bash
    git clone [YOUR-REPOSITORY-URL]
    cd Doc_hub
    ```

2. **Create the Environment File:**
    The project uses a `.env` file in the root directory for configuration. A template is provided.

    ```bash
    cp .env.example .env
    ```

    Now, edit the `.env` file and customize the variables. **It is critical to generate a new `SECRET_KEY`**. You can generate one with `openssl rand -hex 32`.

3. **Build and Run the Containers:**
    This command will build the images for each service and start them in detached mode.

    ```bash
    docker-compose up -d --build
    ```

4. **Create the Initial Admin User:**
    After the containers are up and running, execute the initial data script inside the `app` container.

    ```bash
    docker-compose exec app python app/initial_data.py
    ```

    *Default User:* `admin`
    *Default Password:* `DocHub*2025` (This should be changed in a production environment!)

5. **Access the Application:**
    Open your browser and navigate to `http://localhost:8080/login`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
