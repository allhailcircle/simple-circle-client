from typing import Union, TypeVar, Type, List, Optional
from typing import Union, TypeVar, Type, List, Optional
from uuid import UUID

import aiohttp
from aiohttp import ContentTypeError
from pydantic import parse_obj_as, ValidationError, conint, constr

from models import Error, User, Shape, WackOutput, ShapeUpdate, Message, Reply

T = TypeVar('T')


def _parse_response(model_type: Type[T], data: dict) -> Union[T, Error]:
    if not data:
        return Error(code=500, message="something went wrong")
    try:
        return parse_obj_as(model_type, data)
    except (ValueError, TypeError, ValidationError):
        try:
            return parse_obj_as(Error, data)
        except (ValueError, TypeError, ValidationError):
            return Error(code=500, message=data)


class CircleClient():
    def __init__(self, token):
        header = {'Authorization': f"Bearer {token}"}
        self._session = aiohttp.ClientSession(headers=header)

    async def _get(self, path, *, data=None):
        """Convenience wrapper that supplies a bearer token & returns JSON """
        async with self._session.get(self._url(path), params=self._construct_query(data)) as response:
            try:
                return await response.json()
            except ValueError:
                return {
                    "code": 500,
                    "message": "no_response"
                }
            except ContentTypeError:
                return {
                    "code": response.status,
                    "message": response.message if hasattr(response, "message") else "invalid"
                }

    async def search_users(self,
                           *,
                           contact_info_key: str = None,
                           contact_info_value: str = None,
                           display_name: str = None,
                           n: int = 10) -> Union[Error, List[User]]:
        data = {
            "contact_info_key": contact_info_key,
            "contact_info_value": contact_info_value,
            "display_name": display_name,
            "n": n
        }
        response = await self._get("/users", data=data)
        return _parse_response(List[User], response)

    async def search_shapes(self,
                            *,
                            shape_name: str = None,
                            n: conint(ge=1, le=100) = 10,
                            p: conint(ge=0) = 0) -> Union[Error, List[Shape]]:
        data = {
            "search_string": shape_name,
            "n": n,
            "p": p
        }
        response = await self._get("/shapes", data=data)
        return _parse_response(List[Shape], response)

    async def get_user(self, uuid: UUID) -> Union[Error, User]:
        user = await self._get(f"/users/{str(uuid)}")
        return _parse_response(User, user)

    async def get_shape(self, uuid: UUID) -> Union[Error, Shape]:
        shape = await self._get(f"/shapes/{str(uuid)}")
        return _parse_response(Shape, shape)

    async def _post(self, path, *, data=None):
        """Convenience wrapper that supplies a bearer token & returns JSON """
        async with self._session.post(self._url(path), json=self._construct_query(data)) as response:
            try:
                return await response.json()
            except ValueError:
                return {
                    "code": 500,
                    "message": "no_response"
                }
            except ContentTypeError:
                return {
                    "code": response.status,
                    "message": response.message if hasattr(response, "message") else "invalid"
                }

    async def create_user(self,
                          *,
                          display_name: str,
                          group: bool,
                          contact_info: dict
                          ) -> Union[Error, User]:
        data = {
            "display_name": display_name,
            "group": group,
            "contact_info": contact_info
        }
        user = await self._post("/users", data=data)
        return _parse_response(User, user)

    async def wack(self, shape_id: UUID, user_id: UUID) -> Union[Error, WackOutput]:
        wack = await self._post(f"/shapes/{str(shape_id)}/wack/{str(user_id)}")
        return _parse_response(WackOutput, wack)

    async def send_message(self,
                           *,
                           user_id: UUID,
                           shape_id: UUID,
                           message: constr(max_length=400),
                           sender_id: Optional[UUID] = None,
                           attachment_url: Optional[str] = None):
        data = {
            "user_id": str(user_id),
            "sender_id": str(sender_id) if sender_id else None,
            "shape_id": str(shape_id),
            "message": message,
            "attachment_url": attachment_url
        }
        message = await self._post("/message", data=data)
        return _parse_response(Message, message)

    async def generate_reply(self, shape_id: UUID, user_id: UUID):
        data = {
            "shape_id": str(shape_id),
            "user_id": str(user_id)
        }
        reply = await self._post("/reply", data=data)
        return _parse_response(Reply, reply)

    async def _put(self, path, *, data=None):
        """Convenience wrapper that supplies a bearer token & returns JSON """
        async with self._session.put(self._url(path), json=data) as response:
            try:
                return await response.json()
            except ValueError:
                return {
                    "code": 500,
                    "message": "no_response"
                }
            except ContentTypeError:
                return {
                    "code": response.status,
                    "message": response.message if hasattr(response, "message") else "invalid"
                }

    async def update_user(self, update: User) -> Union[Error, User]:
        update = update.dict()
        update['id'] = str(update['id'])
        user = await self._put(f"/users/{update['id']}", data=update)
        return _parse_response(User, user)

    async def update_shape(self, update: Shape) -> Union[Error, Shape]:
        shape = await self._put(f"/shapes/{str(update.id)}", data=ShapeUpdate(**update.dict()).dict())
        return _parse_response(Shape, shape)

    @staticmethod
    def _url(path):
        """Creates a URL from the environment-specified base URL & a path supplied as a parameter"""
        return f"http://localhost:8000{path}"

    @staticmethod
    def _construct_query(query):
        """Removes falsy fields from a dictionary"""
        if query:
            return {key: value for key, value in query.items() if value is not None}
