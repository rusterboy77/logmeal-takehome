# LogMeal — Technical Take-Home Resolution

Resolution of the LogMeal Take-Home test.

As a student, my previous experience with Python and Flask was limited. However, I took this challenge as an opportunity to learn, adapt quickly, and build a fully functional prototype fulfilling all the core requirements within the 6-8 hours limit.

## 🚀 How to run the project

To start the application, simply run the following command in the root folder:

```bash
docker-compose up --build
```

- The **Frontend** will be available at: `http://localhost:3000`
- The **Backend API** will be running at: `http://localhost:8000`

## 🧠 Trade-offs and Decisions

Given the time constraints and my learning curve with Python, I made the following decisions:
1. **In-Memory Database:** Instead of setting up a full relational database, I used Python dictionaries (`images_db` and `shares_db`) to store records temporarily. 
2. **Analyse Endpoint Mocking:** Since there is no real AI processing available, the `/api/analyse_image` endpoint reads the real file from the File System using `os.path.getsize()` and returns real metadata (file size in KB and original name).
3. **Share Link TTL:** The 10-minute expiration is handled using Python's `datetime` library comparing the current time with the `expires_at` timestamp.

---

# LogMeal — Full-stack Technical Take-Home (Spec-Only Pack)

**Submission window:** 48 h · **Estimated effort:** 6–8 h

Implement a small **API + Front-end** to upload images, list them, and analyse one image by id — plus the **Share Link (10min TTL)** feature.

## What you must build

- Backend (using Python Flask) with at least these endpoints (see `docs/openapi.yaml` documentation):
  - `POST /api/upload_image`
  - `GET  /api/list_images`
  - `POST /api/analyse_image` (must return some information about the image)
  - `POST /api/share_image` (returns `{ token, url, expires_at }`)
  - `GET  /s/{token}` (public HTML page with OG tags)

- Front-end (using at least HTML + CSS + JS) that lets a user:
  - Upload an image, list images, analyse an image.
  - Generate and open a **share link**.

- Containers: `docker-compose up --build` must bring up frontend (3000) and backend (8000) without extra steps (see Docker Compose https://docs.docker.com/compose/).

- README.md file explaining what you developed and including the instructions of how to run the code.

- Submit the code in a Gitlab or Github repository.

## Optional extra tasks

- Basic test suite (pytest or similar) and coverage ≥60%. Include inside 'tests' folder.
- Serve Swagger UI from the backend (using `docs/openapi.yaml`).
- CI (GitHub Actions) that builds containers and runs tests.
- S3-compatible storage (e.g., MinIO in docker-compose).
- i18n EN/ES in the frontend using JSON string tables.
- Strict typing (mypy/tsc) with no errors.

## Fair play

- Do not exceed 6–8 h of effort.
- You may change technologies if you explain it in the README.
- Keep commits small and meaningful.
