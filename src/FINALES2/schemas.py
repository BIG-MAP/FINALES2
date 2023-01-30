''' This file collects all the schemas relevant in FINALES2. This file is subject to extension. '''
import strawberry
import typing
from uuid import UUID, uuid4
import inspect

@strawberry.interface
class ObjectBase:
    def allAttributes(self):
        attributes = inspect.getfullargspec(self.__init__).args
        attributes.remove('self')
        return attributes

    def to_dict(self):
        return self.__dict__

@strawberry.type
class User(ObjectBase):
    def __init__(self, username:str='', password:str='', id:str=uuid4(), usergroups:list[str]=[], **kwargs):
        self.username: str = username
        self.id: UUID = id
        self.password: str = password
        self.usergroups: list[str] = usergroups

@strawberry.type
class AccessToken(ObjectBase):
    access_token:str
    token_type:str

# @strawberry.type
# class Query:
#     user_by_name: typing.List(User) = strawberry.field(resolver=get)
#     users_by_group: typing.List[User]
#     users: typing.List(User)

# u = User(username='a', id=UUID('{12345678-1234-5678-1234-567812345678}'), password='abc', usergroups=['1', '2', '3'], test=1234)
# print(u.allAttributes())
# print(u)
# print(u.name)
# print(list(User.__annotations__.keys()))
# d = u.all_fields()
# print('all fields', d)
# print(u.__dict__)
# print('to dict')
# u.to_dict()