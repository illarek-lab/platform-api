import strawberry
from fastapi import Request
from strawberry.fastapi import GraphQLRouter

from app.projects.c22200163.api.graphql.resolvers.geo_events import GeoEventMutation, GeoEventQuery
from app.projects.c22200163.infra.db.postgres import async_session
from app.projects.c22200163.infra.repositories.geo_event_repo import GeoEventRepository


async def get_context(request: Request):
    async with async_session() as session:
        yield {"repo": GeoEventRepository(session)}


schema = strawberry.Schema(query=GeoEventQuery, mutation=GeoEventMutation)
router = GraphQLRouter(schema, context_getter=get_context)