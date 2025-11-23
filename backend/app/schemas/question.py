from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.question import Question
from config import Config

class ImageSchema(Schema):
    url = fields.String(required=True)
    public_id = fields.String(required=True)

class QuestionSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(load_default=None)
    subject = fields.String(required=True, validate=validate.OneOf(list(Config.SUBJECTS.keys())))
    difficulty = fields.Integer(load_default=3, validate=validate.Range(min=1, max=5))
    status = fields.String(load_default='UNANSWERED', validate=validate.OneOf(['UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW']))
    images = fields.List(fields.Nested(ImageSchema), load_default=list, validate=validate.Length(max=5))
    content_text = fields.String(load_default=None)
    author_id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    attempts = fields.Integer(dump_only=True)
    success_rate = fields.Float(dump_only=True)

    @validates('subject')
    def validate_subject(self, value):
        if value not in Config.SUBJECTS:
            raise ValidationError(f'Invalid subject: {value}')
