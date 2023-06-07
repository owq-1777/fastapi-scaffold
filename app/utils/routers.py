from typing import Any, Callable, Coroutine
from fastapi import Request, Response
from fastapi.routing import APIRoute


class APIContextRoute(APIRoute):

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:

        origin_route_handler = super().get_route_handler()

        async def get_request_handler(request: Request) -> Response:

            response: Response = await origin_route_handler(request)

            return response

        return get_request_handler
