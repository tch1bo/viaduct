import markdown

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask import Markup
from flask.ext.login import current_user

from application import db
from application.page.models import Page, PageRevision, PagePermission

page_module = Blueprint('page', __name__)

@page_module.route('/page/')
@page_module.route('/page/<path:page_path>')
def view_page(page_path=''):
	revision = retrieve_page(page_path)

	if not revision or not 'view' in PagePermission.get_rights(current_user,
		page_path):
		return render_template('page/page_not_found.htm', page=page_path)

	return render_template('page/view_page.htm', revision=revision, page=page_path)

def retrieve_page(page_path=''):
	page = Page.query.filter(Page.path==page_path).first()

	if not page:
		return False

	revision = PageRevision.query.filter(PageRevision.page_id==page.id).order_by(
		PageRevision.id.desc()).first()
	
	if not revision:
		return False

	revision.content = Markup(markdown.markdown(revision.content,
		safe_mode='escape', enable_attributes=False))
	
	return revision


@page_module.route('/page/delete/')
@page_module.route('/page/delete/<path:page_path>')
def delete_page(page_path='', revision=''):
	page = Page.query.filter(Page.path==page_path).first()
	revisions = PageRevision.query.filter(PageRevision.page_id==page.id).all()
	for revision in revisions:
		db.session.delete(revision)
	db.session.delete(page)
	db.session.commit()
	return redirect('/')

@page_module.route('/page/edit/', methods=['GET', 'POST'])
@page_module.route('/page/edit/<path:page_path>', methods=['GET', 'POST'])
def edit_page(page_path=''):
	if not 'edit' in PagePermission.get_rights(current_user, page_path):
		return redirect(url_for('index'))

	page = Page.query.filter(Page.path==page_path).first()
	revision = None

	if page:
		revision = PageRevision.query.filter(PageRevision.page_id==page.id).order_by(
			PageRevision.id.desc()).first()

	if request.method == 'POST':
		title = request.form['title'].strip()
		content = request.form['content'].strip()

		if not page:
			page = Page(page_path)

			db.session.add(page)
			db.session.commit()

		revision = PageRevision(page, current_user, title, content)

		db.session.add(revision)
		db.session.commit()

		flash('The page has been saved.', 'success')

		return redirect(url_for('page.view_page', page_path=page_path))

	return render_template('page/edit_page.htm', revision=revision, page=page_path)

