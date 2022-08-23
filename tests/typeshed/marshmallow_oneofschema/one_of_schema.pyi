from _typeshed import Incomplete
from marshmallow import Schema

class OneOfSchema(Schema):
    type_field: str
    type_field_remove: bool
    type_schemas: Incomplete
    def get_obj_type(self, obj): ...
    def get_data_type(self, data): ...
    def dump(self, obj, *, many: Incomplete | None = ..., **kwargs): ...
    def load(self, data, *, many: Incomplete | None = ..., partial: Incomplete | None = ..., unknown: Incomplete | None = ..., **kwargs): ...
    def validate(self, data, *, many: Incomplete | None = ..., partial: Incomplete | None = ...): ...
