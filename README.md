# CookLens

CookLens is a runnable FastAPI web app that turns leftover ingredients into ranked recipe ideas. It is designed local-first: the default detector is deterministic mock AI, so the full experience works without a paid API or downloaded model. The `FoodDetector` interface is ready for a YOLO or other local implementation later.

## Features

- Optional online recipe lookup through TheMealDB, with local recipe fallback
- Optional online image recognition through an OpenAI-compatible vision API
## Run on Windows

Requires Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:8000. API docs are available at http://127.0.0.1:8000/docs.

If PowerShell blocks activation, run the project with `\.venv\Scripts\python.exe run.py` after installation.

## Deploy publicly with Render

The repository includes `Dockerfile`, `.dockerignore`, and `render.yaml`. Push this project to a GitHub repository, create a new Render Blueprint from that repository, and set `VISION_API_KEY` in Render's environment settings only if online image recognition is desired. Render will provide a public `onrender.com` URL after the build finishes.

The free service uses an ephemeral filesystem, so SQLite data and uploaded files should be treated as demo data. Use a managed PostgreSQL database and persistent storage for production use.

For any Docker host, run:

```sh
docker build -t cooklens .
docker run --rm -p 8000:8000 -e PORT=8000 cooklens
```

## Test

```powershell
pytest -q
```

## API

- `POST /api/analyze`: multipart image analysis
- `POST /api/recipes/recommend`: ingredient and preference-based ranking
- `GET /api/recipes/{id}`: recipe detail
- `POST /api/feedback`: store recipe feedback

Example recommendation body:

```json
{
  "ingredients": [{"name": "rice"}, {"name": "egg"}],
  "preferences": {"taste": "Savory", "max_time": 30}
}
```

## Architecture

`app/ai/detector.py` owns detector abstraction and mock inference. `app/ai/normalizer.py` owns canonical ingredient names. `app/recipes/engine.py` owns matching and ranking. API routes only validate requests and coordinate these services. SQLite is created as `food_rescue.db` on startup.

Images are read in memory for analysis and are not written to the upload directory. Visual analysis cannot guarantee food safety; users should consider storage temperature, storage time, packaging condition, and expiry information.

## Replacing the mock detector

Implement `FoodDetector.detect(image)` in `app/ai/detector.py`, then select that implementation from application configuration. Keep the output as `list[Ingredient]` so the API and recipe engine remain unchanged.
