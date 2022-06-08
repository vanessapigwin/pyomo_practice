from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed


class FileForm(FlaskForm):
    file = FileField('Choose an Excel (.xlsx) file',  validators = [FileRequired(), FileAllowed(['xlsx'], 'Excel files only')])
    submit = SubmitField('Submit', render_kw= {'onsubmit': 'submit();'})

