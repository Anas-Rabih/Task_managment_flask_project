from datetime import datetime, timedelta
from ..models.task import Task
from ..extensions import db

class TaskController:
    @staticmethod
    def create_task(user_id, title, description, due_date, priority, status='pending'):
        """Create a new task with validation"""
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            if due_date < datetime.now().date():
                return False, 'Due date cannot be in the past'
        except ValueError:
            return False, 'Invalid date format. Use YYYY-MM-DD'
        
        if priority not in ['low', 'medium', 'high']:
            return False, 'Invalid priority level'
        
        new_task = Task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status=status,
            user_id=user_id
        )
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return True, 'Task created successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Error creating task: {str(e)}'

    @staticmethod
    def get_user_tasks(user_id, sort_by='due_date_asc', filter_status=None):
        query = Task.query.filter_by(user_id=user_id)
        
        if filter_status:
            query = query.filter_by(status=filter_status)
        
        # Sorting logic
        if sort_by == 'due_date_asc':
            query = query.order_by(Task.due_date.asc())
        elif sort_by == 'due_date_desc':
            query = query.order_by(Task.due_date.desc())
        elif sort_by == 'priority_asc':
            query = query.order_by(
                db.case(
                    {'low': 1, 'medium': 2, 'high': 3},
                    value=Task.priority,
                    else_=0
                ).asc()
            )
        elif sort_by == 'priority_desc':
            query = query.order_by(
                db.case(
                    {'high': 1, 'medium': 2, 'low': 3},
                    value=Task.priority,
                    else_=0
                ).asc()
            )
        elif sort_by == 'created_asc':
            query = query.order_by(Task.created_at.asc())
        elif sort_by == 'created_desc':
            query = query.order_by(Task.created_at.desc())
        
        return query

    @staticmethod
    def get_dashboard_stats(user_id):
        """Get statistics for dashboard summary cards"""
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        stats = {
            'total_tasks': Task.query.filter_by(user_id=user_id).count(),
            'completed': Task.query.filter_by(user_id=user_id, status='completed').count(),
            'overdue': Task.query.filter(
                Task.user_id == user_id,
                Task.status != 'completed',
                Task.due_date < today
            ).count(),
            'due_soon': Task.query.filter(
                Task.user_id == user_id,
                Task.status != 'completed',
                Task.due_date.between(today, next_week)
            ).count()
        }
        
        stats['completion_percentage'] = round(
            (stats['completed'] / stats['total_tasks'] * 100) 
            if stats['total_tasks'] > 0 else 0
        )
        
        return stats

    @staticmethod
    def update_task(task_id, user_id, **kwargs):
        """Update task with validation"""
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return False, 'Task not found'
        
        try:
            if 'due_date' in kwargs:
                due_date = datetime.strptime(kwargs['due_date'], '%Y-%m-%d').date()
                if due_date < datetime.now().date():
                    return False, 'Due date cannot be in the past'
                task.due_date = due_date
            
            if 'priority' in kwargs and kwargs['priority'] not in ['low', 'medium', 'high']:
                return False, 'Invalid priority level'
                
            for field in ['title', 'description', 'priority', 'status']:
                if field in kwargs:
                    setattr(task, field, kwargs[field])
            
            db.session.commit()
            return True, 'Task updated successfully'
        except ValueError:
            return False, 'Invalid date format. Use YYYY-MM-DD'
        except Exception as e:
            db.session.rollback()
            return False, f'Error updating task: {str(e)}'

    @staticmethod
    def get_recent_tasks(user_id, limit=5):
        """Get recently created/modified tasks"""
        return Task.query.filter_by(user_id=user_id)\
                    .order_by(Task.updated_at.desc())\
                    .limit(limit)\
                    .all()

@staticmethod
def search_tasks(user_id, search_term):
    """Search tasks by title or description"""
    return Task.query.filter(
        Task.user_id == user_id,
        db.or_(
            Task.title.ilike(f'%{search_term}%'),
            Task.description.ilike(f'%{search_term}%')
        )
    ).all()
    @staticmethod
    def delete_task(task_id, user_id):
        """Delete a task with error handling"""
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return False, 'Task not found'
        
        try:
            db.session.delete(task)
            db.session.commit()
            return True, 'Task deleted successfully'
        except Exception as e:
            db.session.rollback()
            return False, f'Error deleting task: {str(e)}'