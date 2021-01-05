from flask import Blueprint, render_template
from flask_login import login_required

monitor = Blueprint('monitor', __name__,
                        template_folder='templates/monitor')

@monitor.route('/monitor')
@login_required
def index():
    return render_template('monitor.html')
