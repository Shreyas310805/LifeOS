#!/usr/bin/env python3
import os
from app import create_app, db
from app.models import User, HealthMetric, Task, Fitness, Social, AIInsight

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'HealthMetric': HealthMetric,
        'Task': Task,
        'Fitness': Fitness,
        'Social': Social,
        'AIInsight': AIInsight
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)