from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    tomllib = None  # Python 3.10 and older


def read_project_version_from_pyproject() -> str:
    """
    Read the project version from the pyproject.toml file

    Returns:
        str: The project version

    Example:
        "0.1.0"
    """
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return data["project"]["version"]
