"""Tests del punto de entrada principal."""
from unittest.mock import patch

from ejem1.main import app, main


def test_app_is_fastapi_instance():
    from fastapi import FastAPI

    assert isinstance(app, FastAPI)


def test_main_starts_uvicorn():
    """main() debe delegar el arranque del servidor a uvicorn."""
    with patch("uvicorn.run") as mock_run:
        main()
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args
        assert call_kwargs.args[0] == "ejem1.main:app"
