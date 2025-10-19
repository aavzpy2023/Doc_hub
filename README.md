# Doc_hub: A Self-Hosted, Version-Controlled Documentation Platform

![Python](https://img.shields.io/badge/Python-3.11-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.103-green.svg) ![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-lightgrey.svg)

Doc_hub is a comprehensive web platform for creating, managing, and publishing technical documentation using Markdown. The application is built on a modern tech stack (FastAPI, PostgreSQL, Nginx), fully containerized with Docker, and provides a robust system for automatic version control of every change using Git.

## Core Features

* **Web-Based Markdown Editor:** A rich user interface for writing and previewing Markdown documents directly in the browser (powered by EasyMDE).
* **Automatic Git Versioning:** Every document save triggers a Git commit, providing a complete and auditable change history.
* **User Authentication:** Secure login system based on JWT (OAuth2) with user and admin roles.
* **Static Site Generation:** With a single click, administrators can build and publish a navigable static documentation website using **MkDocs**.
* **PDF Export:** Generate high-quality PDFs from any Markdown document on the fly using **Pandoc**.
* **Robust & Scalable Architecture:** Deployed with Docker Compose, using Nginx as a reverse proxy for the FastAPI backend and for serving the generated static site.

## The Problem It Solves

Development and QA teams need a "single source of truth" for their documentation (user manuals, API guides, testing procedures). Doc_hub centralizes this process, ensuring that all documentation is organized, easy to edit, and version-controlled, thus eliminating the chaos of scattered Word files and outdated versions.

## Technology Architecture

The system follows a microservices-oriented architecture orchestrated by Docker Compose:

1. **`nginx` (Reverse Proxy):** The entry point. It routes traffic to the FastAPI application and serves the static MkDocs site.
2. **`app` (FastAPI Backend):** The application's brain. It manages the API, business logic, authentication, Git interactions, and document generation (PDF/Website).
3. **`db` (Database):** A PostgreSQL instance that stores user data, comments, and document locks.

## Project Status & Roadmap

This project is currently **under active development**. The core functionalities described above are implemented and operational. However, this is a live project with a clear vision for future enhancements.

### Current Status

* [x] User Authentication & Authorization (JWT-based).

* [x] Web-based Markdown Editor with live preview.
* [x] Automatic Git versioning on every save.
* [x] Static site generation with MkDocs.
* [x] On-the-fly PDF export with Pandoc.
* [x] Fully containerized with Docker Compose for easy deployment.

### Future Roadmap

* **Document Locking:** Implement a real-time document locking system to prevent simultaneous edits by different users. The database model (`DocumentLock`) is already in place.
* **Commenting System:** Develop a commenting feature per document, allowing for collaborative review. The database models (`Comment`, `User`) are designed to support this.
* **Full-Text Search:** Integrate a search engine (e.g., Elasticsearch or Whoosh) to allow for powerful full-text searching across all documents.
* **CI/CD Pipeline:** Create a CI/CD pipeline (e.g., with GitHub Actions) to automate testing and deployment.
* **Enhanced User Roles & Permissions:** Develop a more granular permission system (e.g., read, write, admin per project/directory).

## Getting Started

### Prerequisites

* Docker
* Docker Compose

### Installation & Launch

1. **Clone the repository:**

    ```bash
    git clone [YOUR-REPOSITORY-URL]
    cd Doc_hub
    ```

2. **Create the environment file:**
    Copy the `.env.example` file (if you create one) to `.env` and customize the variables. Make sure to change the `SECRET_KEY`.

    ```bash
    # Example .env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=docuhub_db
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
    SECRET_KEY=YOUR_RANDOMLY_GENERATED_SECRET_KEY
    ```

3. **Build and run the containers:**

    ```bash
    docker-compose up -d --build
    ```

4. **Create the initial admin user:**
    The system is designed for a script to create the `admin` user on first run. If you need to do it manually:

    ```bash
    docker-compose exec app python app/initial_data.py
    ```

    *Default User:* `admin`
    *Default Password:* `David*2017` (Change in production!)

5. **Access the application:**
    Open your browser and navigate to `http://localhost:8080/login`.