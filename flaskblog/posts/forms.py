from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Name of the Library', validators=[DataRequired()])
    content = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Library')
class ExperienceForm(FlaskForm):
    etitle = StringField('Name of the Experience', validators=[DataRequired()])
    econtent = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Experience')
    virtual_tour = SubmitField('Virtual Tour')
    switching_perspective = SubmitField('Switching Perspective')
    conversation = SubmitField('Conversation')
    
