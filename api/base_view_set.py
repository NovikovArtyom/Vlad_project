import uuid
from typing import Tuple

from django.db import connection
from django.db.models import Field
from django.db.models.query import RawQuerySet
from rest_framework import response, viewsets, status
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response

from api.models import Role


class BaseViewSet(viewsets.ModelViewSet):
    search_fields = []
    table_name = None
    admin_role = Role.objects.get(title='ADMIN')

    def list(self, request, *args, **kwargs):
        order = request.query_params.get('order', 'id')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        search = str(request.query_params.get('search', ''))
        user_id = request.query_params.get('user', None)

        queryset, total = self.query_builder(
            table_name=self.table_name,
            order=order,
            page=page,
            limit=limit,
            search=search,
            user=user_id
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

    def query_builder(self, table_name: str, order: str, page: int, limit: int, search: str, user: uuid) -> Tuple[
        RawQuerySet, int]:
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

        conditions = []

        if search and self.search_fields:
            search_conditions = []
            for field in self.search_fields:
                search_conditions.append(f'LOWER({field}) LIKE LOWER(%s)')
                params.append(f'%{search}%')
                count_params.append(f'%{search}%')
            conditions.append('(' + ' OR '.join(search_conditions) + ')')

        if user is not None:
            conditions.append('user_id = %s')
            params.append(str(user).replace('-', ''))
            count_params.append(str(user).replace('-', ''))

        if conditions:
            where_clause = ' WHERE ' + ' AND '.join(conditions)
            data_query += where_clause
            count_query += where_clause

        data_query += f' ORDER BY {order} LIMIT %s OFFSET %s'
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if (instance.user.id != request.user.id) and (self.admin_role not in request.user.role.all()):
            raise PermissionDenied(
                "У вас нет прав для редактирования этой сущности. Только автор или администратор может изменять сущность.",
                code=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if (instance.user.id != request.user.id) and (self.admin_role not in request.user.role.all()):
            raise PermissionDenied(
                "У вас нет прав для удаления этой сущности. Только автор или администратор может изменять сущность.",
                code=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response({"data": "ok"}, status=status.HTTP_200_OK)
