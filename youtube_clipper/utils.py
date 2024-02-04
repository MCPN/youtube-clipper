from youtube_clipper.converters.registry import CONVERTERS_REGISTRY
from youtube_clipper.parsers.registry import PARSERS_REGISTRY


def get_available_formats() -> list[str]:
    """Get all available formats from converters and parsers registries"""
    return list(map(lambda ext: ext.removeprefix('.'), CONVERTERS_REGISTRY.keys() | PARSERS_REGISTRY.keys()))
