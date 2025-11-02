from fastapi.routing import APIRoute

from app.api.endpoints import api_router
from app.main import app


def test_all_api_routes_are_mounted_with_prefix():
    """
    Vérifie que toutes les routes définies dans api_router sont montées dans l'app principale.
    Gère le préfixe /v1 et ignore les routes système.
    """
    prefix = "/v1"

    # Routes du router (non préfixées)
    expected_paths = {
        prefix + route.path
        for route in api_router.routes
        if isinstance(route, APIRoute)
    }

    # Routes réelles montées dans l'app (filtrées)
    app_paths = {route.path for route in app.routes if isinstance(route, APIRoute)}

    missing = expected_paths - app_paths
    assert not missing, f"Routes manquantes dans app.main : {missing}"
