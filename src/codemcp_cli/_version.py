from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("codemcp-cli")
except PackageNotFoundError:
    __version__ = "0+unknown"
