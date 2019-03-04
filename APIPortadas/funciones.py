#----------------------------------#
# -   Funciones de Aplicación    - #
#----------------------------------#
import os, sys
import json, re, urllib.request
from os import walk
from datetime import datetime
from .configuracion import dict, ruta, hostData


def revisarExtension(nombreArchivo):
    return '.' in nombreArchivo and \
        nombreArchivo.rsplit('.', 1)[1].lower() in dict['EXTENSIONES']


def guardarArchivo(archivo, nombreArchivo, ruta):
    path = dict['DIR_UPLOAD']+ruta
    archivo.save(os.path.join(path, nombreArchivo))


def getCarpeta(clasificacion):
    bandera = re.match(r'([\d]{1,3})', clasificacion, re.M|re.I)
    if bandera:
        return '000/'
    else:
        return clasificacion+'/'


def getClasificacion(clasificacion):
    data = re.compile(r'(\d)\w+').split(clasificacion, 2)
    bandera = re.match(r'([\d]{1,3})', data[0], re.M|re.I)
    if bandera:
        return '000'
    else:
        return data[0]


def getUrl(carpeta, nombreArchivo):
    return os.path.join(dict['DIR_UPLOAD']+carpeta, nombreArchivo)


def getIsbn(nombreArchivo):
    arreglo = nombreArchivo.split('.')
    return arreglo[0]


def getImageIsbn(isbn):
    data = isbn.split()
    data = re.compile(r'(\()').split(data[0], 2)
    return data[0]


def cleanStatus(s):
    data = re.compile(r'(\n)').split(s, 2)
    return data[0]


def getExtension(nombreArchivo):
    arreglo = nombreArchivo.split('.')
    return arreglo[-1]


def getParametros(url):
    data = url.split('?', 2)
    return data[1]


def getListaArchivos(carpeta):
    ruta = dict['DIR_UPLOAD'] + carpeta
    lista = []
    for(_, _, archivos) in walk(ruta):
        lista.extend(archivos)
    return lista


def getUrlImagen(clase, id):
    if(re.match(r'([\d]{1,3})', clase, re.M|re.I)):
        clase = '000'
    else:
        clase = re.compile(r'(\D)+').split(clase, 2)
    path = dict['DIR_UPLOAD'] + ruta['img'] + '/' + clase + '/'
    extensiones = []
    bandera = False
    for root, dirs, files in os.walk(path):
        for archivo in files:
            nombreArchivo, extension = archivo.split('.')
            if id == nombreArchivo:
                bandera = True
    if bandera:
        #http://localhost:52214/img/AE/8423945006
        return "http://" + hostData['HOST']+":"+hostData['PORT']+"/static/" + clase.upper() + "/" + archivo
    return None


def getArregloUrls(nombreArchivo):
    path = os.path.join(dict['DIR_UPLOAD']+ruta['txt'], nombreArchivo)
    data = []
    with open(path) as archivo:
        for linea in archivo:
            arreglo = linea.split(',')
            registro = {
                'isbn': getImageIsbn(arreglo[0]),
                'clasificacion': getClasificacion(arreglo[1]),
                'url': arreglo[2],
                'parametros' : getParametros(arreglo[2]),
                'status': cleanStatus(arreglo[3])
                }
            data.append(registro)
    archivo.close()
    return data


def getArregloUrlJson(nombreArchivo):
    path = os.path.join(dict['DIR_UPLOAD']+ruta['txt'], nombreArchivo)
    data = []

    with open(path, 'r') as archivo:
        datos = json.load(archivo)
        for registro in datos['portadas']:
            data.append(json.loads(registro))
    archivo.close()
    return data

    
    
    with open(path, 'r') as archivo:
        datos = json.load(archivo)
        for registro in datos['portadas']:
            data.append(json.loads(registro))
    archivo.close()
    return data


def descargarImagen(clase, isbn, url):
    urlImg = 'http://books.google.com/books/content?'+url
    path = dict['DIR_UPLOAD'] + ruta['img'] +'/'+ clase +'/'+ isbn + '.jpg'
    logPath = os.path.join(dict['DIR_UPLOAD']+ruta['log'], 'Errores.txt')
    try:
        urllib.request.urlretrieve(urlImg, path)
    except Exception as ex:
        with open(logPath, 'a') as archivoError:
            archivoError.write("Error: " + ex.args[0] + "\nFecha: " + str(datetime.now()))
        archivoError.close()
    if os.path.isfile(path):
        return 1, path 
    else:
        return 0, 'El archivo no pudo ser descargado'


def actualizarArchivo(nombreArchivo, isbn, estatus):
    path = os.path.join(dict['DIR_UPLOAD']+ruta['txt'], nombreArchivo)
    jsonData = {}
    jsonData['portadas'] = []
    if os.path.isfile(path):
        data = getArregloUrlJson(nombreArchivo)
        for registro in data:
            if registro['isbn'] == isbn:
                registro['status'] = estatus
            jsonData['portadas'].append(json.dumps(registro, sort_keys=False))
        with open(path, 'w') as archivoJson:
            json.dump(jsonData, archivoJson)
    return None


def cleanLine(linea):
    data = ''
    data = re.sub(r'\((.*?)\)', '', linea)
    return data


def archivoJson(nombreArchivo):
    path = os.path.join(dict['DIR_UPLOAD']+ruta['txt'], nombreArchivo)
    logPath = os.path.join(dict['DIR_UPLOAD']+ruta['log'], 'Errores.txt')
    rejectedPath = os.path.join(dict['DIR_UPLOAD']+ruta['txt'], 'Rejected.txt')
    data = []
    with open(path, mode='r', encoding="utf8") as archivo:
        numLinea = 1
        cadenaExcepcion = ''
        cadenaRechazada = ''
        for linea in archivo:
            linea = cleanLine(linea)
            arreglo = linea.split(',')
            try:
                registro = {
                'isbn': getImageIsbn(arreglo[0]),
                'clasificacion': getClasificacion(arreglo[1]),
                'url': arreglo[2],
                'parametros' : getParametros(arreglo[2]),
                'status': cleanStatus(arreglo[3])
                }
                data.append(registro)
            except Exception as x:
                cadenaExcepcion += "Error: " + x.args[0] + "\nFecha: " + str(datetime.now()) + "\nLinea: [" + str(numLinea) + "] - " + linea
                cadenaRechazada += linea
            numLinea += 1
        if cadenaExcepcion:
            with open(logPath, 'a') as archivoError:
                archivoError.write(cadenaExcepcion)
            archivoError.close()
        if cadenaRechazada:
            with open(rejectedPath, 'a') as archivoRechazo:
                archivoRechazo.write(cadenaRechazada)
            archivoRechazo.close()
    archivo.close()
    os.remove(path)
    jsonData = {}
    jsonData['portadas'] = []
    nombreLista, extension = nombreArchivo.split('.')
    path = os.path.join(dict['DIR_UPLOAD']+ruta['txt'], nombreLista + '.json')
    for registro in data:
        jsonData['portadas'].append(json.dumps(registro, sort_keys=False))
    with open(path, 'w') as archivoJson:
        json.dump(jsonData, archivoJson)
    return None