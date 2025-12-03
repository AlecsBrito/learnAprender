"""
Utilitários compartilhados para painel administrativo.
Centraliza lógica comum entre vocab e exercises admin views.
"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def get_paginated_queryset(queryset, page_number, per_page=25):
    """
    Pagina um queryset.
    
    Args:
        queryset (QuerySet): QuerySet a paginar
        page_number (int/str): Número da página
        per_page (int): Itens por página (padrão: 25)
    
    Returns:
        Page: Objeto de página do paginator
    """
    paginator = Paginator(queryset, per_page)
    try:
        return paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        return paginator.page(1)


def filter_by_search_and_level(queryset, search_query, level_value, search_fields):
    """
    Filtra queryset por busca de texto e nível.
    
    Args:
        queryset (QuerySet): QuerySet base
        search_query (str): Texto de busca
        level_value (str): Nível a filtrar
        search_fields (list): Lista de nomes de campos para busca (ex: ['word', 'translation'])
    
    Returns:
        QuerySet: QuerySet filtrado
    """
    if search_query:
        q_search = Q()
        for field in search_fields:
            q_search |= Q(**{f"{field}__icontains": search_query})
        queryset = queryset.filter(q_search)
    
    if level_value:
        queryset = queryset.filter(level=level_value)
    
    return queryset


def filter_by_category(queryset, category_value):
    """
    Filtra queryset por categoria.
    
    Args:
        queryset (QuerySet): QuerySet base
        category_value (str): Categoria a filtrar
    
    Returns:
        QuerySet: QuerySet filtrado
    """
    if category_value:
        queryset = queryset.filter(category__icontains=category_value)
    return queryset


def filter_by_sharing(queryset, shared_filter):
    """
    Filtra queryset por compartilhamento (shared/personal/all).
    
    Args:
        queryset (QuerySet): QuerySet base
        shared_filter (str): 'shared', 'personal', ou None para todos
    
    Returns:
        QuerySet: QuerySet filtrado
    """
    if shared_filter == 'shared':
        return queryset.filter(is_shared=True)
    elif shared_filter == 'personal':
        return queryset.filter(is_shared=False)
    return queryset
