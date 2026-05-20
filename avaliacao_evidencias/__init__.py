from __future__ import annotations

__all__ = ["AnaliseCandidata", "inventariar_analises"]


def __getattr__(name: str):
    if name in __all__:
        from .pipeline import AnaliseCandidata, inventariar_analises

        values = {
            "AnaliseCandidata": AnaliseCandidata,
            "inventariar_analises": inventariar_analises,
        }
        return values[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
