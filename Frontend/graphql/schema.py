import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType

from ..models import *


# class Author(SQLAlchemyObjectType):
#     class Meta:
#         model = AuthorModel
#         interfaces = (relay.Node, )


# class File(SQLAlchemyObjectType):
#     class Meta:
#         model = FileModel
#         interfaces = (relay.Node, )


class Addon(SQLAlchemyObjectType):
    class Meta:
        model = AddonModel
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    addons = graphene.List(Addon)

    def resolve_addons(self, info):
        query = Addon.get_query(info)  # SQLAlchemy query
        return query.all()

    # files = graphene.List(File)

    # def resolve_files(self, info):
    #     query = File.get_query(info)  # SQLAlchemy query
    #     return query.all()

    # node = relay.Node.Field()
    # all_addons = SQLAlchemyConnectionField(Addon)

    # node = relay.Node.Field()
    # all_employees = SQLAlchemyConnectionField(Employee)
    # all_roles = SQLAlchemyConnectionField(Role)
    # role = graphene.Field(Role)


schema = graphene.Schema(query=Query, types=[Addon])
