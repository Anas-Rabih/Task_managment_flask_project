from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..controllers.auth_controller import AuthController
from ..controllers.task_controller import TaskController
from datetime import datetime
from ..models.task import Task 
from ..extensions import db
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from ..forms.task_forms import TaskForm  # Add this import

from ..controllers.auth_controller import AuthController
task_bp = Blueprint('task', __name__)

@task_bp.route('/dashboard')
def dashboard():
    user = AuthController.get_current_user()
    if not user:
        flash('Please login to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get sorting and filtering parameters
    sort_by = request.args.get('sort_by', 'due_date_asc')
    filter_status = request.args.get('filter_status')
    
    # Get tasks and stats from TaskController
    tasks = TaskController.get_user_tasks(user.id, sort_by, filter_status)
    stats = TaskController.get_dashboard_stats(user.id)
    
    # Create form instance
    form = TaskForm()
    
    # Check for modal parameter
    open_modal = request.args.get('openModal')
    
    return render_template('dashboard.html', 
                            tasks=tasks, 
                            stats=stats,
                            form=form,
                            current_sort=sort_by,
                            current_filter=filter_status,
                            open_modal=open_modal)

@task_bp.route('/task/add', methods=['POST'])
def add_task():
    user = AuthController.get_current_user()
    if not user:
        flash('Please login to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    form = TaskForm()
    if form.validate_on_submit():
        try:
            success, message = TaskController.create_task(
                user.id,
                form.title.data,
                form.description.data,
                form.due_date.data.strftime('%Y-%m-%d'),
                form.priority.data,
                form.status.data
            )
            flash(message, 'success' if success else 'danger')
        except Exception as e:
            flash(f'Error creating task: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'danger')
    
    return redirect(url_for('task.dashboard'))

@task_bp.route('/task/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    user = AuthController.get_current_user()
    if not user:
        flash('Please login to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        # Validate CSRF token first
        validate_csrf(request.form.get('csrf_token'))
        
        success, message = TaskController.update_task(
            task_id,
            user.id,
            title=request.form['title'],
            description=request.form.get('description', ''),
            due_date=request.form['due_date'],
            priority=request.form.get('priority', 'medium'),
            status=request.form.get('status', 'pending')
        )
        
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('task.dashboard'))
        
    except ValidationError:
        flash('CSRF token missing or invalid', 'danger')
        return redirect(url_for('task.dashboard'))
    except Exception as e:
        flash(f'Error updating task: {str(e)}', 'danger')
        return redirect(url_for('task.dashboard')) 
       
@task_bp.route('/task/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    user = AuthController.get_current_user()
    if not user:
        flash('Please login to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    task = Task.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('task.dashboard'))
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting task: {str(e)}', 'danger')
    
    return redirect(url_for('task.dashboard'))

@task_bp.route('/api/tasks', methods=['GET'])
def api_get_tasks():


    user = AuthController.get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    tasks = TaskController.get_user_tasks(user.id)
    tasks_data = [{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.isoformat(),
        'priority': task.priority,
        'status': task.status,
        'created_at': task.created_at.isoformat()
    } for task in tasks]
    
    return jsonify(tasks_data)

@task_bp.route('/api/tasks', methods=['POST'])
def api_create_task():


    user = AuthController.get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    success, message = TaskController.create_task(
        user.id,
        data.get('title'),
        data.get('description'),
        data.get('due_date'),
        data.get('priority')
    )
    
    if not success:
        return jsonify({'error': message}), 400
    
    return jsonify({'message': message}), 201

@task_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):

    user = AuthController.get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    success, message = TaskController.delete_task(task_id, user.id)
    if not success:
        return jsonify({'error': message}), 404
    
    return jsonify({'message': message}), 200