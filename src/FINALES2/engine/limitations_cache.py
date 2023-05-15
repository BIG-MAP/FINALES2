from typing import Any, Dict, List

from FINALES2.server.schemas import LimitationsInfo


class LimitationsCache:
    """Class to manage the limitations of the server."""

    def __init__(self):
        """Initialize internal cache"""
        self._internal_cache = {}

    def add_limitations(self, limitations: Dict[str, Any]):
        """Add limitations to the cache."""

        if "quantity" not in limitations:
            raise ValueError(
                f"[CORRUPTED DB] no quantity identifier in limitations: {limitations}"
            )
        quantity = limitations["quantity"]

        if "method" not in limitations:
            raise ValueError(
                f"[CORRUPTED DB] no method identifier in limitations: {limitations}"
            )
        method = limitations["method"]

        if quantity not in self._internal_cache:
            self._internal_cache[quantity] = {}

        if method not in self._internal_cache[quantity]:
            self._internal_cache[quantity][method] = []

        self._internal_cache[quantity][method].append(limitations["properties"])

    def get_limitations(self) -> List[LimitationsInfo]:
        """Get a list of consolidated limitations."""
        limitations_list = []
        for quantity, quantity_data in self._internal_cache.items():
            for method, method_data in quantity_data.items():
                for limitations in method_data:
                    limitations_list.append(
                        LimitationsInfo(
                            quantity=quantity,
                            method=method,
                            limitations=limitations,
                        )
                    )
        return limitations_list
