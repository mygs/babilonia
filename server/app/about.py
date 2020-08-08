from flask import Blueprint, render_template
from flask_login import login_required

about_system = Blueprint('about', __name__,
                        template_folder='templates')

@about_system.route('/about')
@login_required
def index():
    return render_template('about_system.html')
