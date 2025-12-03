"""
Utilitários compartilhados para painel administrativo de exercises.
Importa funções genéricas de vocab/admin_utils.py.
"""

from vocab.admin_utils import (
    get_paginated_queryset,
    filter_by_search_and_level,
    filter_by_category,
    filter_by_sharing,
)

__all__ = [
    'get_paginated_queryset',
    'filter_by_search_and_level',
    'filter_by_category',
    'filter_by_sharing',
]
