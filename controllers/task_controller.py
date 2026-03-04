"""
Controlador de Tareas - Maneja la lógica de negocio de las tareas

Este archivo contiene todas las rutas y lógica relacionada con las tareas.
Representa la capa "Controlador" en la arquitectura MVC.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models.task import Task
from app import db


def register_routes(app):
    """
    Registra todas las rutas del controlador de tareas en la aplicación Flask
    
    Args:
        app (Flask): Instancia de la aplicación Flask
    """
    
    @app.route('/')
    def index():
        """
        Ruta principal - Redirige a la lista de tareas
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        return redirect(url_for('task_list'))
    
    
    @app.route('/tasks')
    def task_list():
        """
        Muestra la lista de todas las tareas

        Query Parameters:
            filter (str): Filtro para mostrar tareas ('all', 'pending', 'completed')
            sort (str): Ordenamiento ('date', 'title', 'created')

        Returns:
            str: HTML renderizado con la lista de tareas
        """
        # Implementar en Versión 1
        # Query the database for all tasks
        tasks = Task.query.all()

        # Apply filtering
        if filter_type == 'pending':
            tasks = [task for task in tasks if not task.completed]
        elif filter_type == 'completed':
            tasks = [task for task in tasks if task.completed]

        # Apply sorting
        if sort_by == 'title':
            tasks.sort(key=lambda t: t.title)
        elif sort_by == 'date':
            tasks.sort(key=lambda t: t.due_date or datetime.max)

        # Count tasks by status
        pending_count = sum(1 for task in tasks if not task.completed)
        completed_count = sum(1 for task in tasks if task.completed)
        # Obtener parámetros de filtro y ordenamiento
        filter_type = request.args.get('filter', 'all')
        sort_by = request.args.get('sort', 'created')

        # Por ahora, solo mostrar una lista vacía
        tasks = []

        # Datos para pasar a la plantilla
        context = {
            'tasks': tasks,
            'filter_type': filter_type,
            'sort_by': sort_by,
            'total_tasks': len(tasks),
            'pending_count': 0,
            'completed_count': 0
        }

        return render_template('task_list.html', **context)
 
    
    @app.route('/tasks/new', methods=['GET', 'POST'])
    def task_create():
        """
        Crea una nueva tarea
        
        GET: Muestra el formulario de creación
        POST: Procesa los datos del formulario y crea la tarea
        
        Returns:
            str: HTML del formulario o redirección tras crear la tarea
        """
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            due_date_str = request.form.get('due_date')

            # Validar que el título sea obligatorio
            if not title:
                flash('El título es obligatorio', 'error')
                return render_template('task_form.html')

            # Convertir la fecha de vencimiento si existe
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Formato de fecha inválido. Debe ser YYYY-MM-DD', 'error')
                    return render_template('task_form.html')

            # Crear la nueva tarea
            new_task = Task(title=title, description=description, due_date=due_date)
            new_task.save()

            flash('Tarea creada exitosamente', 'success')
            return redirect(url_for('task_list'))

        # Mostrar formulario de creación
        return render_template('task_form.html')
    
    @app.route('/tasks/<int:task_id>')
    def task_detail(task_id):
        """
        Muestra los detalles de una tarea específica
        
        Args:
            task_id (int): ID de la tarea a mostrar
        
        Returns:
            str: HTML con los detalles de la tarea
        """
        pass # TODO: implementar el método
    
    
    @app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
    def task_edit(task_id):
        """
        Edita una tarea existente
        
        Args:
            task_id (int): ID de la tarea a editar
        
        GET: Muestra el formulario de edición con datos actuales
        POST: Procesa los cambios y actualiza la tarea
        
        Returns:
            str: HTML del formulario o redirección tras editar
        """
        if request.method == 'POST':
            title = request.form.get('title')
        
        # Mostrar el formulario para editar la tarea
        task = Task.query.get(task_id)
        if not task:
            flash('Tarea no encontrada', 'error')
            return redirect(url_for('task_list'))
        return render_template('task_form.html', task=task)
    
    
    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    def task_delete(task_id):
        """
        Elimina una tarea
        
        Args:
            task_id (int): ID de la tarea a eliminar
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        task = Task.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
        flash('Tarea eliminada exitosamente', 'success')
        return redirect(url_for('task_list'))
    
    
    @app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
    def task_toggle(task_id):
        """
        Cambia el estado de completado de una tarea
        
        Args:
            task_id (int): ID de la tarea a cambiar
        
        Returns:
            Response: Redirección a la lista de tareas
        """
        task = Task.query.get(task_id)
        if task:
            task.completed = not task.completed
            db.session.commit()
        flash('Estado de tarea actualizado exitosamente', 'success')
        return redirect(url_for('task_list')) 
    
    
    # Rutas adicionales para versiones futuras
    
    @app.route('/api/tasks', methods=['GET'])
    def api_tasks():
        """
        API endpoint para obtener tareas en formato JSON
        (Para versiones futuras con JavaScript)
        
        Returns:
            json: Lista de tareas en formato JSON
        """
        return jsonify({
            'tasks': [],
            'message': 'API en desarrollo - Implementar en versiones futuras'
        })
    
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404 - Página no encontrada"""
        return render_template('404.html'), 404
    
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        db.session.rollback()
        return render_template('500.html'), 500

