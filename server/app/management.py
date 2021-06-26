from datetime import date
import simplejson as json
from werkzeug.local import LocalProxy
from flask import current_app, Blueprint, render_template, request, abort
from sqlalchemy import exc
from flask_login import login_required
from Models import DB, Crop, Supplier

logger = LocalProxy(lambda: current_app.logger)
management = Blueprint("management", __name__, template_folder="templates/management")


@management.route("/management")
@login_required
def index():
    crops = DB.session.query(Crop)
    # modules = database.retrieve_modules()
    # plants = database.retrieve_plants()
    # return render_template('management.html', crops=crops, modules=modules, plants=plants)
    return render_template("management.html", crops=crops)


@management.route("/management/module")
def module():
    # modules = database.retrieve_modules()
    # oasis = database.retrieve_oasis()
    # return render_template('module.html', modules=modules , oasis=oasis)
    return render_template("module.html")


@management.route("/management/crop-module", methods=["GET"])
@login_required
def cropmodule():
    code = request.args.get("code")
    return database.retrive_crop_module(id)


###############################################################################
################################ SUPPLIER #####################################
###############################################################################


@management.route("/management/supplier")
@login_required
def supplier():
    suppliers = DB.session.query(Supplier)
    return render_template("supplier.html", suppliers=suppliers)


@management.route("/management/save-supplier", methods=["POST"])
@login_required
def save_supplier():
    supplier = Supplier(request.get_json())
    logger.info("[SAVE SUPPLIER] %s", request.get_json())
    DB.session.merge(supplier)
    return json.dumps({"message": "Supplier was saved successfully"}), 200


###############################################################################
################################ GUI UTILS ####################################
###############################################################################
@management.context_processor
def utility_processor():
    def crop_duration(value):
        today = date.today()
        difference_in_days = abs((today - value).days)
        return difference_in_days

    return {"crop_duration": crop_duration}


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)
