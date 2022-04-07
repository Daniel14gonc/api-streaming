from urllib import response
from flask import jsonify


def admin_getCuenta(cursor):
    query = "SELECT correo, activo FROM cuenta order by correo;"
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response = []
    for elements in cuentas:
        new_obj = {'correo': elements[0], 'activo' : elements[1]}
        response.append(new_obj)
    return jsonify(response)

def admin_activado(cursor, content, connection):
    query1 = "select activo from cuenta where correo='%s';"%(content['correo'])
    cursor.execute(query1)
    valor = cursor.fetchall()
    if(valor[0][0]==True):
        query = "update cuenta set activo = False where correo='%s';"%(content['correo'])
        cursor.execute(query)
    else:
        query = "update cuenta set activo = True where correo='%s';"%(content['correo'])
        cursor.execute(query)

    return jsonify({'message': 'success'})

def admin_getestrellas(cursor):
    query = "SELECT nombre FROM estrellas order by nombre;"
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response = []
    for elements in cuentas:
        new_obj = {'nombre': elements[0]}
        response.append(new_obj)
    return jsonify(response)

def admin_getanunciantes(cursor):
    query = "SELECT nombre FROM anunciante order by nombre;"
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response = []
    for elements in cuentas:
        new_obj = {'nombre': elements[0]}
        response.append(new_obj)
    return jsonify(response)

def admin_getanuncios(cursor):
    query = "SELECT id, id_anunciante FROM anuncios order by id;"
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response = []
    for elements in cuentas:
        new_obj = {'id': elements[0], 'anunciante': elements[1]}
        response.append(new_obj)
    return jsonify(response)

def admin_getcont(cursor):
    query = "SELECT nombre FROM contenido order by nombre;"
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response = []
    for elements in cuentas:
        new_obj = {'nombre': elements[0]}
        response.append(new_obj)
    return jsonify(response)