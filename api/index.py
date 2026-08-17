from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware

BASE_DIR = Path(__file__).parent.parent

# Replace this with the new application URL when you have it.
APPLY_URL = "https://forms.gle/KUrigKv3yvz9tSgz7"


class CacheStaticMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/assets/fonts/") or path.startswith("/images/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif path.startswith("/assets/"):
            response.headers["Cache-Control"] = "public, max-age=3600, must-revalidate"
        return response


app = FastAPI(title="Carolina Skylab", description="Carolina Skylab Site")
app.add_middleware(CacheStaticMiddleware)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals["apply_url"] = APPLY_URL


@app.get("/favicon.ico")
def favicon():
    return FileResponse(
        str(BASE_DIR / "static" / "images" / "logo.png"),
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "static" / "assets")), name="assets")
app.mount("/images", StaticFiles(directory=str(BASE_DIR / "static" / "images")), name="images")


@app.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {"active": "home"})


@app.get("/apply")
def apply_redirect():
    return RedirectResponse(APPLY_URL, status_code=307)


@app.get("/contact")
def contact_redirect():
    return RedirectResponse("/#contact", status_code=307)


@app.get("/projects", response_class=HTMLResponse)
def projects(request: Request):
    return templates.TemplateResponse(request, "projects.html", {"active": "projects"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
