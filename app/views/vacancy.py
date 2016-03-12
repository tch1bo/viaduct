from flask import Blueprint, render_template, request, redirect, url_for,\
    abort, flash

from sqlalchemy import or_, and_, func

from datetime import datetime

from app import app, db
from app.utils import flash_form_errors
from app.models.vacancy import Vacancy
from app.models.company import Company
from app.forms import VacancyForm
from app.api.module import ModuleAPI

blueprint = Blueprint('vacancy', __name__, url_prefix='/vacancies')
FILE_FOLDER = app.config['FILE_DIR']


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/<int:page_nr>/', methods=['GET', 'POST'])
def view_list(page_nr=1):
    if not ModuleAPI.can_read('vacancy'):
        return abort(403)

    # Order the vacancies in such a way that vacancies that are new
    # or almost expired, end up on top.
    order = func.abs(
        (100 * (func.datediff(Vacancy.start_date, func.current_date()) /
                func.datediff(Vacancy.start_date, Vacancy.end_date))) - 50)

    if request.args.get('search') is not None:
        search = request.args.get('search')

        vacancies = Vacancy.query.join(Company).\
            filter(or_(Vacancy.title.like('%' + search + '%'),
                   Company.name.like('%' + search + '%'),
                   Vacancy.workload.like('%' + search + '%'),
                   Vacancy.contract_of_service.like('%' + search + '%'))).\
            order_by(order.desc())

        if not ModuleAPI.can_write('vacancy'):
            vacancies = vacancies.filter(and_(Vacancy.start_date <
                                         datetime.utcnow(), Vacancy.end_date >
                                         datetime.utcnow())).paginate(page_nr,
                                                                      15, True)
        else:
            for i, vacancy in enumerate(vacancies):
                if (vacancy.start_date < datetime.date(datetime.utcnow()) and
                        vacancy.end_date < datetime.date(datetime.utcnow())):
                    vacancies[i].expired = True

            vacancies = vacancies.paginate(page_nr, 15, False)

        return render_template('vacancy/list.htm', vacancies=vacancies,
                               search=search, path=FILE_FOLDER,
                               title="Vacatures")

    if not ModuleAPI.can_write('vacancy'):
        vacancies = Vacancy.query.order_by(
            order.desc()).filter(and_(Vacancy.start_date <
                                 datetime.utcnow(), Vacancy.end_date >
                                 datetime.utcnow())).paginate(page_nr,
                                                              15, True)
    else:
        vacancies = Vacancy.query.join(Company).filter().\
            order_by(order.desc())

        for i, vacancy in enumerate(vacancies):
            if (vacancy.start_date < datetime.date(datetime.utcnow()) and
                    vacancy.end_date < datetime.date(datetime.utcnow())):
                vacancies[i].expired = True

        vacancies = vacancies.paginate(page_nr, 15, False)

    return render_template('vacancy/list.htm', vacancies=vacancies,
                           search="", path=FILE_FOLDER, title="Vacatures")


@blueprint.route('/create/', methods=['GET'])
@blueprint.route('/edit/<int:vacancy_id>/', methods=['GET'])
def edit(vacancy_id=None):
    '''
    FRONTEND
    Create, view or edit a vacancy.
    '''
    if not ModuleAPI.can_read('vacancy'):
        return abort(403)

    # Select vacancy.
    if vacancy_id:
        vacancy = Vacancy.query.get(vacancy_id)
    else:
        vacancy = Vacancy()

    form = VacancyForm(request.form, vacancy)

    # Add companies.
    form.company_id.choices = [(c.id, c.name) for c in Company.query.
                               order_by('name')]

    return render_template('vacancy/edit.htm', vacancy=vacancy, form=form,
                           title="Vacatures")


@blueprint.route('/create/', methods=['POST'])
@blueprint.route('/edit/<int:vacancy_id>/', methods=['POST'])
def update(vacancy_id=None):
    '''
    BACKEND
    Create, view or edit a vacancy.
    '''
    if not ModuleAPI.can_write('vacancy'):
        return abort(403)

    # Select vacancy.
    if vacancy_id:
        vacancy = Vacancy.query.get(vacancy_id)
    else:
        vacancy = Vacancy()

    form = VacancyForm(request.form, vacancy)

    # Add companies.
    form.company_id.choices = [(c.id, c.name) for c in Company.query.
                               order_by('name')]

    if form.validate_on_submit():
        vacancy.title = form.title.data
        vacancy.description = form.description.data
        vacancy.start_date = form.start_date.data
        vacancy.end_date = form.end_date.data
        vacancy.contract_of_service = form.contract_of_service.data
        vacancy.workload = form.workload.data
        vacancy.company = Company.query.get(form.company_id.data)

        db.session.add(vacancy)
        db.session.commit()

        if vacancy_id:
            flash('Vacature opgeslagen', 'success')
        else:
            vacancy_id = vacancy.id
            flash('Vacature aangemaakt', 'success')
    else:
        error_handled = False
        if not form.title.data:
            flash('Geen titel opgegeven', 'danger')
            error_handled = True
        if not form.description:
            flash('Geen beschrijving opgegeven', 'danger')
            error_handled = True
        if not form.start_date:
            flash('Geen begindatum opgegeven', 'danger')
            error_handled = True
        if not form.end_date:
            flash('Geen einddatum opgegeven', 'danger')
            error_handled = True
        if not form.workload:
            flash('Geen werklast opgegeven', 'danger')
            error_handled = True

        if not error_handled:
            flash_form_errors(form)

    return redirect(url_for('vacancy.edit', vacancy_id=vacancy_id))


@blueprint.route('/delete/<int:vacancy_id>/', methods=['POST'])
def delete(vacancy_id):
    '''
    BACKEND
    Delete a vacancy.
    '''
    if not ModuleAPI.can_write('vacancy'):
        return abort(403)

    vacancy = Vacancy.query.get(vacancy_id)
    if not vacancy:
        return abort(404)

    db.session.delete(vacancy)
    db.session.commit()
    flash('Vacature verwijderd', 'success')

    return redirect(url_for('vacancy.view_list'))