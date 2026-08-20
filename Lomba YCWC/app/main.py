from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes_analysis import router as analysis_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_recipes import router as recipes_router
from app.database.database import SessionLocal, init_db
from app.database.seed import seed_db

BASE_DIR = Path(__file__).resolve().parent
@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seed_db(db)
        yield
    finally:
        db.close()


app = FastAPI(title="CookLens", description="Turn leftovers into delicious meals.", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.include_router(analysis_router)
app.include_router(recipes_router)
app.include_router(feedback_router)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, name="index.html", context={"request": request})


@app.get("/main")
def main_page(request: Request):
    return templates.TemplateResponse(request, name="index.html", context={"request": request})


@app.get("/scan")
def scan(request: Request):
    return templates.TemplateResponse(request, name="scan.html", context={"request": request})


@app.get("/recipes")
def recipes(request: Request):
    return templates.TemplateResponse(request, name="recipes.html", context={"request": request})


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse(request, name="about.html", context={"request": request})


@app.get("/recipes/{recipe_id}")
def recipe_page(request: Request, recipe_id: int):
    return templates.TemplateResponse(request, name="recipe.html", context={"request": request, "recipe_id": recipe_id})
