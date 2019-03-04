#---------------------------------#
# -   Rutas de la Applicación   - #
#---------------------------------#
from datetime import datetime
from flask import flash, jsonify, make_response, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
from APIPortadas import app
from .funciones import *
from .configuracion import dict, ruta

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Inicio',
        year=datetime.now().year,
    )


@app.route('/contact')
def contacto():
    """Renders the contact page."""
    return render_template(
        'contacto.html',
        title='Contacto',
        year=datetime.now().year,
        message='Pagina de Contacto.'
    )


@app.route('/acerca')
def acerca():
    """Renders the about page."""
    return render_template(
        'acerca.html',
        title='Acerca',
        year=datetime.now().year,
        message='Acerca de la herramienta de Portadas'
    )


@app.route('/lista', methods=['GET', 'POST'])
def lista():
    """Renders the about page."""
    title = "Cargar listado de portadas"
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Error en la carga del archivo')
            return redirect(request.url)
        archivo = request.files['file']

        if archivo.filename == '':
            flash('No se selecciono un archivo')
            return redirect(request.url)

        if archivo and revisarExtension(archivo.filename):
            nombreArchivo = secure_filename(archivo.filename)
            guardarArchivo(archivo, nombreArchivo, ruta['txt'])
            archivoJson(nombreArchivo)
            return render_template(
                'lista.html',
                title=title,
                year=datetime.now().year,
                message='Listado: '+nombreArchivo+' subido correctamente.',
                status='OK'
            )
    else:
        return render_template(
            'lista.html',
            title=title,
            year=datetime.now().year,
            message='Subir listado de portadas por descargar'
        )


@app.route('/listado', methods=['GET', 'POST'])
def listado():
    """Renders the list page."""
    return render_template(
        'listado.html',
        title='Prueba',
        year=datetime.now().year,
        message='Acerca de la herramienta de Portadas'
    )


@app.route('/portada', methods=['GET', 'POST'])
def portada():
    """Renders the about page."""
    title = 'Imagenes de portada'
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Error en la carga del archivo')
            return redirect(request.url)
        archivo = request.files['file']

        if archivo.filename == '':
            flash('No se selecciono un archivo')
            return redirect(request.url)

        if archivo and revisarExtension(archivo.filename):
            nombreArchivo = secure_filename(archivo.filename)
            if re.search(r'^[A-Z]{1,3}[_][0-9]{10,13}[.][a-z]{3}', nombreArchivo):
                clasificacion, nombreArchivo = nombreArchivo.split('_')
                carpeta = getCarpeta(clasificacion)
                rutaArchivo = ruta['img'] +'/' + carpeta
                #Guardar archivo
                guardarArchivo(archivo, nombreArchivo, rutaArchivo)
                #Obtener url
                imgurl = getUrlImagen(clasificacion, getIsbn(nombreArchivo))
                isbn = getIsbn(nombreArchivo)
                extension = getExtension(nombreArchivo)
                msj ='Listado: '+nombreArchivo+' subido correctamente.'
            else:
                nombreArchivo, isbn, extension, clasificacion, imgurl = '', '', '', '', ''
                msj = 'No se guardo el archivo'

            return render_template(
                'portada.html',
                title=title,
                year=datetime.now().year,
                message= msj,
                nombrePortada=nombreArchivo,
                clasificacion=clasificacion,
                isbn=isbn,
                extension=extension,
                imgurl=imgurl
            )

    return render_template(
        'portada.html',
        title=title,
        year=datetime.now().year,
        message='Herramienta para subir portadas para resguardo.'
    )


@app.route('/portada/<clase>/<id>', methods=['GET', 'POST'])
def portadaImg(clase, id):
    title = 'Portada descargada'
    path = getUrlImagen(clase, id)
    if path:
        nombreArchivo = id + '.jpg'
        return render_template(
            'descarga.html',
            title=title,
            year=datetime.now().year,
            message='Herramienta para obtener las imagenes de portada desde Internet.',
            clasificacion=clase,
            isbn=isbn, 
            url=path
            )
    else:
        return render_template(
            'descarga.html',
            title=title,
            year=datetime.now().year,
            message='No existe la portada.',
            )


@app.route('/contador', methods=['GET', 'POST'])
def contador():
    """Renders the contador page."""
    title = "Herramienta de control de descargas"
    if request.method == 'POST':
        archivoSeleccionado = request.form['listaArchivos']
        if archivoSeleccionado:
            listaUrls = getArregloUrlJson(archivoSeleccionado)
        return render_template(
            'contador.html',
            title=title,
            year=datetime.now().year,
            message='Estado de descargas',
            listaArchivos = getListaArchivos(ruta['txt']),
            listaDescargas = archivoSeleccionado,
            listaUrls = listaUrls,
            archivoSeleccionado = archivoSeleccionado
        )
    else:
        return render_template(
            'contador.html',
            title=title,
            year=datetime.now().year,
            message='Herramienta para obtener las imagenes de portada desde Internet.',
            listaArchivos = getListaArchivos(ruta['txt']),
            archivoSeleccionado = ""
        )


@app.route('/descarga/<lista>/<clase>/<isbn>/<param>', methods=['GET', 'POST'])
def descarga(lista, clase, isbn, param):
    title = "Verificación de Descarga"
    if request.method == 'GET':
        bandera = descargarImagen(clase, isbn, param)
        actualizarRegistro(lista, isbn)
        return render_template(
            'descarga.html',
            title=title,
            year=datetime.now().year,
            message='Herramienta para obtener las imagenes de portada desde Internet.',
            clasificacion=clase,
            isbn=isbn, 
            url='http://books.google.com/books/content?'+param
            )
    else:
        status, url = descargarImagen(clase, isbn, param)
        actualizarRegistro(lista, isbn)
        data = {
            'status': status, 
            'clasificacion' : clase, 
            'isbn' : isbn, 
            'url': url 
            }
        return make_response(jsonify(data), 200)


@app.route('/img/<clase>/<id>')
def buscarImagen(clase, id):
    """Return the URL for the image"""
    path = getUrlImagen(clase, id)
    if path:
        data = {'url' : path }
    else:
        data =  {'code': 404, 'mensaje' : "Archivo no encontrado" }
    return make_response(jsonify(data), 200)


@app.route('/actualizar/<nom>/<id>')
def actualizarRegistro(nom, id):
    """Actualizar el status de la imagen """
    actualizarArchivo(nom, id, '1')
    data = { 'code': 200 , 'mensaje': 'Actualizado' }
    return make_response(jsonify(data), 200)