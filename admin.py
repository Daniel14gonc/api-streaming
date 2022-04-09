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

def get_premios(cursor):
    query = "SELECT * FROM premios;"
    cursor.execute(query)
    data = cursor.fetchall()
    response = []
    for elements in data:
        new_obj = {'nombre': elements[0]}
        response.append(new_obj)

    return jsonify(response)


def crear_pelicula(connection, cursor, content):
    content = content['data']
    list = []
    for elements in content:
        list.append(elements)
  
  
    query = "SELECT id FROM director WHERE nombre='%s';"%(list[2])
    cursor.execute(query)
    id_d = cursor.fetchall()[0][0]
    
    query = "SELECT id FROM contenido order by id desc limit 1;"
    cursor.execute(query)
    id = int(cursor.fetchall()[0][0]) + 1
    
    query = "INSERT INTO contenido VALUES ('%s', '%s', '%s', '%s', %s, '%s', '%s');"%(id, list[0], list[1], id_d, list[3], list[4], list[5])
    cursor.execute(query)
    connection.commit()

    for elements in list[6]:
        query = "SELECT id FROM estrellas WHERE nombre='%s';"%(elements)
        cursor.execute(query)
        id_e = cursor.fetchall()[0][0]
        
        query = "INSERT INTO actuan VALUES ('%s' , '%s');"%(id, id_e)
        cursor.execute(query)
        connection.commit()

    return jsonify({'message':'success'})

def delete_contenido(connection, cursor, nombre):
    query = "DELETE FROM contenido WHERE nombre = '%s';"%(nombre)
    cursor.execute(query)
    connection.commit()

    return jsonify({'message': 'success'})


def crear_anunciante(connection, cursor, content):
    content = content['data']


    query = "SELECT id FROM anunciante order by id desc limit 1;"
    cursor.execute(query)
    id = int(cursor.fetchall()[0][0]) + 1
  
    query = "insert into anunciante values ('%s' , '%s');"%(id,content)
    cursor.execute(query)

    connection.commit()

    return jsonify({'message':'success'})

def crear_anuncio(connection, cursor, content):
    link = content['link']
    anunciante = content['anunciante']

    query = "SELECT id FROM anunciante where nombre='%s';"%(anunciante)
    cursor.execute(query)
    id_anun = cursor.fetchall()[0][0]

    query = "SELECT id FROM anuncios order by id desc limit 1;"
    cursor.execute(query)
    id = int(cursor.fetchall()[0][0]) + 1

    if(id<10):
        id="0"+str(id)
  
    query = "insert into anuncios values ('%s' , '%s', '%s');"%(id,id_anun, link)
    cursor.execute(query)

    connection.commit()

    return jsonify({'message':'success'})

def get_todopeli(nombre, cursor):
    query = "select d.nombre , c.duracion, c.link, c.imagen from contenido c join director d on d.id=c.id_director where c.nombre='%s';"%(nombre)
    cursor.execute(query)
    elements = cursor.fetchall()
    response = {'nombre': elements[0][0], 'duracion' : elements[0][1],'link' : elements[0][2],'imagen' : elements[0][3]}
    return jsonify(response)

def update_peli(cursor, connection, content):
    content = content['data']

    query1 = "SELECT id FROM director WHERE nombre = '%s'"%(content[1])
    cursor.execute(query1)
    id = cursor.fetchall()[0][0]

    query = "UPDATE contenido SET nombre = '%s', id_director = '%s', duracion = '%s', link = '%s', imagen = '%s' WHERE nombre = '%s'"%(content[0], id, content[2], content[3], content[4], content[5])
    cursor.execute(query)
    connection.commit()

    return jsonify({"message":"success"})