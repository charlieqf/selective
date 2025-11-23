from app import ma
from app.models.user import User
from marshmallow import fields, validate

class RegisterSchema(ma.Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=64))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))

class LoginSchema(ma.Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
