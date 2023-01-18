import os
import logging
import ntpath
import shutil
import random

from flask import render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename

from inn_app import app, utils


@app.route('/')
def index():
    session.clear()
    return render_template('index.html')


@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['filename']
        filename = secure_filename(file.filename)
        if utils.allowed_file(filename, app.config['ALLOWED_EXTENSIONS']):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            return render_template('index.html', error="Выбран неверный тип файла")
    try:
        utils.get_pdf(os.path.join(
            app.config['UPLOAD_FOLDER'], filename), app.config['TEMPORARY_FOLDER'])
        return redirect(url_for('fill_doc'))
    except BaseException as e:
        logging.exception(e)
        return render_template('index.html', error=e)


@app.route('/fill_doc', methods=['GET', 'POST'])
def fill_doc():
    DocClass = utils.getClassByFilPreifx(session['cl'])
    tmp_file_path = session['tmp_file']
    text_document = open(tmp_file_path, 'r')
    text = text_document.read()
    text_document.close()

    cl = DocClass()
    cl.get_data(text)
    cl.save_to_db()
    cl_name = cl.__class__.__name__
    if request.method == 'GET':
        data = cl.checkIfExist()
        if(data):
            return render_template(f'fill-doc-{cl_name}.html', page_title='Запись уже существует', data=data)
        else:
            return render_template(f'fill-doc-{cl_name}.html', data=['', '', '', '', ''])
    else:
        cl.update(data=request.form.to_dict())
        try:
            os.remove(session['tmp_file'])
        except:
            pass
        return render_template('ok.html')

@app.route('/rko', methods=['GET'])
def rko():
	inn = request.args['inn']
	podpisant = request.args['podpisant']
	hash = ''
	try:
		hash = ntpath.basename(session['tmp_file'])
		hash = os.path.splitext(hash)[0]
	except BaseException as e:
		hash = "%032x" % random.getrandbits(128)
	try:
		utils.RKO(
			inn,
			podpisant,
			app.config['TEMPLATES_FOLDER'],
			app.config['TREATIES_FOLDER'],
			hash
		)
		shutil.make_archive(f'{app.config["TREATIES_FOLDER"]}/{hash}', "zip", app.config['TREATIES_FOLDER'], hash)
		shutil.rmtree(f'{app.config["TREATIES_FOLDER"]}/{hash}', ignore_errors=False)
		session.clear()
		return send_file(f'{app.config["TREATIES_FOLDER"]}/{hash}.zip', as_attachment=True)
	except BaseException as e:
		logging.exception(e)
		return render_template('index.html', error=e)
