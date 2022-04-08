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
        query = "update cuenta set activo = false where correo='%s';"%(content['correo'])
        cursor.execute(query)
    else:
        query = "update cuenta set activo = true where correo='%s';"%(content['correo'])
        cursor.execute(query)
    connection.commit()

    return jsonify({'message': 'success'})

def admin_getestrellas(cursor):
    query = "SELECT id, nombre FROM estrellas order by nombre;"
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response = []
    for elements in cuentas:
        new_obj = {'id': elements[0], 'nombre': elements[1]}
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
    query = "SELECT a.id, an.nombre, an.id FROM anuncios a join anunciante an on a.id_anunciante = an.id order by a.id;"
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

def edit_star(connection, cursor, content):
    query = "UPDATE estrellas SET nombre = '%s' where id='%s';"%(content['nombre'], content['id'])
    cursor.execute(query)
    connection.commit()
    
    return jsonify({'message': 'success'})


def change_anunciante(connection, cursor, content):
    query = "SELECT id FROM anunciante where nombre = '%s';"%(content['anunciante'])
    cursor.execute(query)
    datos = cursor.fetchall()
    ida = datos[0][0]

    query = "UPDATE anuncios set id_anunciante = '%s' where id='%s'"%(ida, content['id'])
    cursor.execute(query)
    connection.commit()

    return jsonify({'message': 'success'})

def delete_anuncios(connection, cursor, id):

    query = "DELETE FROM anuncios WHERE id = '%s';"%(id)
    cursor.execute(query)
    connection.commit()

    return jsonify({'message': 'success'})

def change_correo(connection, cursor, content):
    print(content)
    query = "UPDATE cuenta set correo = '%s' where correo='%s'"%(content['new'], content['old'] )
    cursor.execute(query)
    connection.commit()

    return jsonify({'message': 'success'})

def change_anunciante2(connection, cursor, content):
    query = "UPDATE anunciante set nombre = '%s' where nombre='%s'"%(content['new'], content['old'])
    cursor.execute(query)
    connection.commit()

    return jsonify({'message': 'success'})

def delete_anunciante(connection, cursor, nombre):
    query = "DELETE FROM anunciante WHERE nombre = '%s';"%(nombre)
    print(query)
    cursor.execute(query)
    connection.commit()

    return jsonify({'message': 'success'})