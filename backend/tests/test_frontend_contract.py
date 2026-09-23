import re
from pathlib import Path

from app.api.routes import router


def _strip_template_exprs(path: str) -> str:
    """Ganti setiap `${...}` (termasuk yang bersarang) dengan placeholder.

    Template literal bisa bersarang, mis.
    `` `/buyers/portal/${qs ? `?${qs}` : ''}` `` — regex naif `\\$\\{[^}]+\\}`
    salah menangkapnya sehingga menghasilkan path rusak. Fungsi ini menelusuri
    kedalaman kurung kurawal agar seluruh ekspresi tergantikan.
    """
    out: list[str] = []
    i = 0
    n = len(path)
    while i < n:
        if path.startswith("${", i):
            depth = 1
            j = i + 2
            while j < n and depth:
                if path.startswith("${", j):
                    depth += 1
                    j += 2
                    continue
                if path[j] == "}":
                    depth -= 1
                j += 1
            # Ekspresi yang memuat query string (`?...`) tidak memengaruhi path.
            expr = path[i:j]
            out.append("" if "?" in expr else "{}")
            i = j
            continue
        out.append(path[i])
        i += 1
    return "".join(out)


def _normalize(path: str) -> str:
    path = path.replace("/api/v1", "")
    path = _strip_template_exprs(path)
    path = re.sub(r"\{[^}]+\}", "{}", path)
    # Abaikan query string (e.g. `?language=${language}`) — tidak memengaruhi path route.
    path = path.split("?", 1)[0]
    return path


def _route_pattern(path: str) -> re.Pattern:
    return re.compile("^" + re.escape(_normalize(path)).replace(r"\{\}", "[^/]+") + "$")


def _iter_api_fetch_calls(text: str):
    """Ambil setiap pemanggilan apiFetch beserta argumen path & opsinya.

    Path bisa berupa string biasa atau template literal yang bersarang
    (mis. `` `...${qs ? `?${qs}` : ''}` ``), sehingga pencocokan naif dengan
    `` `[^`]+` `` akan terpotong di backtick dalam. Fungsi ini menelusuri
    literal secara manual dengan memperhatikan kedalaman `${...}`.
    """
    for call in re.finditer(r"apiFetch(?:<[^>]+>)?\(", text):
        i = call.end()
        while i < len(text) and text[i] in " \t\n\r":
            i += 1
        if i >= len(text):
            continue
        quote = text[i]
        if quote in "`'\"":
            j = i + 1
            depth = 0
            while j < len(text):
                ch = text[j]
                if ch == "\\":
                    j += 2
                    continue
                if quote == "`" and text.startswith("${", j):
                    depth += 1
                    j += 2
                    continue
                if quote == "`" and ch == "}" and depth:
                    depth -= 1
                elif ch == quote and depth == 0:
                    break
                j += 1
            raw = text[i + 1 : j]
            rest = text[j + 1 :]
            semi = rest.find(";")
            opts = rest if semi == -1 else rest[:semi]
            yield raw, opts


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
        for raw, opts in _iter_api_fetch_calls(text):
            path = _normalize(raw)
            method_match = re.search(r"method:\s*['\"]([A-Z]+)['\"]", opts)
            method = method_match.group(1) if method_match else "GET"
            if not any(method == route_method and pattern.match(path) for route_method, pattern in backend_routes):
                missing.append(f"{method} {path} from {file.name}")

    assert missing == []
