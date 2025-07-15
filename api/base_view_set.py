from typing import Tuple

from django.db import connection, OperationalError
from django.db.models import Field
from django.db.models.query import RawQuerySet
from rest_framework import response, viewsets
from rest_framework.exceptions import ValidationError


class BaseViewSet(viewsets.ModelViewSet):
    search_fields = []
    table_name = None

    def list(self, request, *args, **kwargs):
        order = request.query_params.get('order', 'id')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        search = str(request.query_params.get('search', ''))

        queryset, total = self.query_builder(
            table_name=self.table_name,
            order=order,
            page=page,
            limit=limit,
            search=search
        )

        serializer = self.get_serializer(queryset, many=True)

        return response.Response({
            'data': serializer.data,
            'meta': {
                'current_page': page,
                'last_page': (total + limit - 1) // limit,
                "per_page": limit,
                'total': total
            }
        })


    def query_builder(self, table_name: str, order: str, page: int, limit: int, search: str) -> Tuple[RawQuerySet, int]:
        valid_order_fields = self.get_valid_order_fields()
        if order.lstrip('-') not in valid_order_fields:
            raise ValidationError(
                detail={
                    'error': f'Недопустимое поле для сортировки: {order}',
                    'available_fields': valid_order_fields
                },
                code=400
            )

        data_query = f'SELECT * FROM {table_name}'
        count_query = f'SELECT COUNT(*) FROM {table_name}'
        params = []
        count_params = []

        if search and self.search_fields:
            conditions = []
            for field in self.search_fields:
                conditions.append(f'"{field}" LIKE %s')
                params.append(f'%{search}%')
                count_params.append(f'%{search}%')

            where_clause = " WHERE " + " OR ".join(conditions)
            data_query += where_clause
            count_query += where_clause

        data_query += f" ORDER BY {order} LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])

        with connection.cursor() as cursor:
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()[0]

        return self.queryset.model.objects.raw(data_query, params), total


    def get_valid_order_fields(self):
        return [
            f.name for f in self.queryset.model._meta.get_fields()
            if isinstance(f, Field) and not f.is_relation
        ]