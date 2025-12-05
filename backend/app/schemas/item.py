from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.item import Item
from config import Config

class ImageSchema(Schema):
    url = fields.String(required=True)
    public_id = fields.String(required=True)
    rotation = fields.Integer(load_default=0, validate=validate.OneOf([0, 90, 180, 270]))

class ItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(load_default=None)
    
    # Legacy subject support (Optional)
    subject = fields.String(load_default=None)
    
    # New Collection support
    collection_id = fields.Integer(load_default=None)
    
    difficulty = fields.Integer(load_default=3, validate=validate.Range(min=1, max=5))
    status = fields.String(load_default='UNANSWERED', validate=validate.OneOf(['UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW']))
    images = fields.List(fields.Nested(ImageSchema), load_default=list, validate=validate.Length(max=5))
    content_text = fields.String(load_default=None)
    author_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    attempts = fields.Integer(dump_only=True)
    success_rate = fields.Float(dump_only=True)
    # Tags accepted on input but handled by to_dict() for output
    tags = fields.List(fields.String(), load_default=list, load_only=True)

    # We can keep subject validation if provided, but it's not required anymore
    @validates('subject')
    def validate_subject(self, value):
        if value and value not in Config.SUBJECTS:
            raise ValidationError(f'Invalid subject: {value}')
