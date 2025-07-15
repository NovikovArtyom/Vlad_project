from django.db import connection
from django.db.models.query import RawQuerySet
from rest_framework import viewsets, response
from rest_framework.fields import Field

from api.models import Article
from api.serializers import ArticleSerializer


class BaseViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        order = request.query_params.get('order', 'id')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        search = request.query_params.get('search', '')
        table_name = self.queryset.model._meta.db_table

        queryset = self.query_builder(
            table_name=table_name,
            order=order,
            page=page,
            limit=limit,
            search=search
        )

        serializer = self.get_serializer(queryset, many=True)
        total = 10

        return response.Response({
            'data': serializer.data,
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'last_page': (total + limit - 1) // limit
            }
        })


    def query_builder(self, table_name: str, order: str, page: int, limit: int, search: str) -> RawQuerySet:
        query = f'SELECT * FROM {table_name}'
        params = []

        if search:
            model = self.queryset.model
            fields = [f.name for f in model._meta.get_fields()
                      if isinstance(f, Field) and not f.is_relation]

            search_conditions = []
            for field in fields:
                search_conditions.append(f"{field}::text LIKE %s")
                params.append(f"%{search}%")

            query += " WHERE " + " OR ".join(search_conditions)

        query += f" ORDER BY {order} LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])

        return self.queryset.model.objects.raw(query, params)


    # def get_total_count(self, table_name: str, search: str = '') -> int:
    #     query = f'SELECT COUNT(*) FROM {table_name}'
    #     params = []
    #
    #     if search:
    #         query += ' WHERE name LIKE %s'
    #         params.append(f'%{search}%')
    #
    #     with connection.cursor() as cursor:
    #         cursor.execute(query, params)
    #         return cursor.fetchone()[0]


class ArticleViewSet(BaseViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
