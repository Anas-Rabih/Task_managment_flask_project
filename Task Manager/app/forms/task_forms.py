from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime
from wtforms.validators import DataRequired, Length, ValidationError
class TaskForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message="Title is required"),
        Length(max=100, message="Title cannot exceed 100 characters")
    ])
    
    description = TextAreaField('Description', validators=[
        Length(max=500, message="Description cannot exceed 500 characters")
    ])
    
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[
        DataRequired(message="Due date is required")
    ])
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='pending')

    # Optional custom validator for due date
    def validate_due_date(self, field):
        if field.data < datetime.now().date():
            raise ValidationError("Due date cannot be in the past")