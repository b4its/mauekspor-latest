import re
from pathlib import Path

from app.api.routes import router


def _normalize(path: str) -> str:
    path = path.replace("/api/v1", "")
    path = re.sub(r"\$\{[^}]+\}", "{}", path)
    path = re.sub(r"\{[^}]+\}", "{}", path)
    return path


def _route_pattern(path: str) -> re.Pattern:
    return re.compile("^" + re.escape(_normalize(path)).replace(r"\{\}", "[^/]+") + "$")


def test_frontend_api_contract_is_covered():
    frontend_api = Path(__file__).resolve().parents[2] / "frontend" / "src" / "lib" / "api"
    backend_routes = []
    for route in router.routes:
        methods = getattr(route, "methods", None)
        if not methods:
            continue
        for method in methods:
            if method in {"GET", "POST", "PATCH", "DELETE", "PUT"}:
                backend_routes.append((method, _route_pattern(route.path)))

    missing = []
    for file in sorted(frontend_api.glob("*.ts")):
        text = file.read_text()
        for match in re.finditer(r"apiFetch(?:<[^>]+>)?\((`[^`]+`|'[^']+'|\"[^\"]+\")(?P<opts>[^;]*?)\)", text, re.S):
            path = _normalize(match.group(1)[1:-1])
            method_match = re.search(r"method:\s*['\"]([A-Z]+)['\"]", match.group("opts"))
            method = method_match.group(1) if method_match else "GET"
            if not any(method == route_method and pattern.match(path) for route_method, pattern in backend_routes):
                missing.append(f"{method} {path} from {file.name}")

    assert missing == []
