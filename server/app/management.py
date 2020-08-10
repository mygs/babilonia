from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required
from Models import DB, Crop

management = Blueprint('management', __name__,
                        template_folder='templates/management')

@management.route('/management')
@login_required
def index():
    crops = DB.session.query(Crop)
    #modules = database.retrieve_modules()
    #plants = database.retrieve_plants()
    #return render_template('management.html', crops=crops, modules=modules, plants=plants)
    return render_template('management.html', crops=crops)

@management.route('/management/module')
def module():
    #modules = database.retrieve_modules()
    #oasis = database.retrieve_oasis()
    #return render_template('module.html', modules=modules , oasis=oasis)
    return render_template('module.html')

@management.route('/management/supplier')
def supplier():
    suppliers = DB.session.query(Supplier)
    return render_template('supplier.html', suppliers=suppliers)

@management.route('/management')
@login_required
def index():
    crops = DB.session.query(Crop)
    #modules = database.retrieve_modules()
    #plants = database.retrieve_plants()
    #return render_template('management.html', crops=crops, modules=modules, plants=plants)
    return render_template('management.html', crops=crops)



@management.route('/management/crop-module', methods=['GET'])
@login_required
def cropmodule():
    code = request.args.get('code');
    return database.retrive_crop_module(id)


@management.context_processor
def utility_processor():
    def crop_duration(value):
        today = date.today()
        difference_in_days = abs((today - value).days)
        return difference_in_days
    return {
            'crop_duration':crop_duration
            }
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)
