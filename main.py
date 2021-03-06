from random import random
from flask import Flask, request, json
from flask_cors import CORS, cross_origin
from flask import jsonify
from config import config
import psycopg2
from psycopg2 import extensions
from perfiles import *
from contenido_premios import *
from contenido_sugerido import *
from admin import *
from datetime import datetime
import socket

connection = psycopg2.connect(user="postgres",
                                  password="ketchup14",
                                  host="streaming.cddkmwmgfell.us-east-1.rds.amazonaws.com",
                                  port="5432",
                                  database="Streaming")

s = socket.fromfd(connection.fileno(), socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 6)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)

cursor = connection.cursor()


def create_app(enviroment):
    app = Flask(__name__)

    app.config.from_object(enviroment)

    return app

enviroment = config['development']
app = create_app(enviroment)
cors = CORS(app)

@app.route('/api/directores', methods=['GET'])
def get_directores():
    postgreSQL_select_Query = "select * from director"
    cursor.execute(postgreSQL_select_Query)
    directores = cursor.fetchall()
    response = []
    for elements in directores:
        new_obj = {'id': elements[0], 'nombre': elements[1]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/directores', methods=['POST'])
def add_directores():
    content = request.json
    lista = []
    for keys in content:
        lista.append(str(content[keys]))
    sql = "INSERT INTO director VALUES(%s, %s)"
    cursor.execute(sql,lista)
    connection.commit()
    response = {'message': 'success 200'}
    return jsonify(response)

@app.route('/api/signin', methods=['GET'])
def signin():
    correo = request.headers.get('correo')
    password = request.headers.get('password')
    postgreSQL_select_Query = "SELECT passw FROM cuenta WHERE correo=%s and activo = true;"
    cursor.execute(postgreSQL_select_Query, [correo])
    data = cursor.fetchall()
    response = {'message' : 'error 401'}
    if data:
        passw = data[0][0]
        if(passw==password):
            response = {'message': 'success 200'}
        else:
            time = datetime.now()
            quericito = "INSERT INTO intentos VALUES (%s,%s);"
            cursor.execute(quericito, [correo, time])
            connection.commit()
            response = {'message' : 'error 409'}

    return jsonify(response)

@app.route('/api/logon', methods=['POST'])
def logon():
    conn = psycopg2.connect(user="postgres",
                                  password="ketchup14",
                                  host="streaming.cddkmwmgfell.us-east-1.rds.amazonaws.com",
                                  port="5432",
                                  database="Streaming")
    serializable = extensions.ISOLATION_LEVEL_SERIALIZABLE
    conn.set_isolation_level(serializable)
    cursor = conn.cursor()
    content = request.json
    datos = []
    for keys in content:
        datos.append(content[keys])
    datos.append(content['correo'])
    postgreSQL_select_Query = "SELECT correo FROM cuenta WHERE correo= %s"
    cursor.execute(postgreSQL_select_Query, [content['correo']])
    data = cursor.fetchall()
    if (not data):
        sql = "insert into cuenta values (%s, %s, %s, true, current_timestamp, 'insert', %s);"
        cursor.execute(sql, datos)
        conn.commit()
        response = {'message': 'success'}
    else:
        response = {'message': 'error 409'}
    conn.close()
    return jsonify(response)

@app.route('/api/signinAdmin', methods=['GET'])
def signinAdmin():
    correo = request.headers.get('correo')
    password = request.headers.get('password')
    postgreSQL_select_Query = "SELECT passw FROM administrador WHERE correo= %s;"
    cursor.execute(postgreSQL_select_Query, [correo])
    data = cursor.fetchall()
    print(data)
    if data:
        passw = data[0][0]
        if(passw==password):
            response = {'message': 'success'}
        else:
            response = {'message': 'error 404'}
    else:
        response = {'message': 'error 404'}

    return jsonify(response)

@app.route('/api/logonAdmin', methods=['POST'])
def logonAdmin():
    content = request.json
    datos = []
    for keys in content:
        datos.append(content[keys])
    postgreSQL_select_Query = "SELECT correo FROM administrador WHERE correo= %s;"
    cursor.execute(postgreSQL_select_Query, [content['correo']])
    data = cursor.fetchall()
    if (not data):
        sql = "insert into administrador values (%s, %s);"
        cursor.execute(sql, [datos])
        connection.commit()
        response = {'message': 'success'}
    else:
        response = {'message': 'error 409'}

    return jsonify(response)

@app.route('/api/perfiles', methods=['POST'])
def add_perfiles():
    content = request.json
    
    return crear_perfil(content)

@app.route('/api/perfiles', methods=['GET'])
def get_perfiles():
    content = request.headers.get('correo')
    
    return get_profiles(cursor, content)

@app.route('/api/perfiles', methods=['PUT'])
def update_perfiles():
    content = request.json
    conn1 = psycopg2.connect(user="postgres",
                                  password="ketchup14",
                                  host="streaming.cddkmwmgfell.us-east-1.rds.amazonaws.com",
                                  port="5432",
                                  database="Streaming")
    serializable = extensions.ISOLATION_LEVEL_SERIALIZABLE
    conn1.set_isolation_level(serializable)
    cursor = conn1.cursor()
    
    return actualizar_perfil(cursor, content, conn1)

@app.route('/api/contenido', methods=['GET'])
def get_contenido():
    nombre = request.headers.get('nombre')
    nombre = '%' + nombre + '%'

    megaQuery = f'''select nombre, link, imagen from contenido where nombre ILIKE %s
                    union
                    SELECT distinct(c.nombre), c.link, c.imagen FROM contenido c JOIN pertenece p on c.id = p.id_contenido WHERE p.nombre_genero ILIKE %s
                    union
                    SELECT distinct(c.nombre), c.link, c.imagen FROM contenido c JOIN actuan a on c.id = a.id_contenido JOIN estrellas e on a.id_estrella = e.id WHERE e.nombre ILIKE %s
                    union
                    select distinct(c.nombre), c.link, c.imagen from premiacion p join contenido c on c.id = p.id_contenido where p.nombre_premio ILIKE %s
                    union
                    select nombre, link, imagen from contenido where cast(fecha_estreno as varchar) like %s
                    union
                    select distinct(p.nombre), p.link, p.imagen from director d join contenido p on d.id=p.id_director 
                    where d.nombre ilike %s;

    '''

    cursor.execute(megaQuery, [nombre, nombre, nombre, nombre, nombre, nombre])
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1], "imagen":elements[2]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/contenido_generos', methods=['GET'])
def get_contenido_by_genero():
    genero = request.headers.get('genero')
    postgreSQL_select_Query = "SELECT c.nombre, c.link FROM contenido c JOIN pertenece p on c.id " + "=" +" p.id_contenido WHERE p.nombre_genero ILIKE %s;"
    cursor.execute(postgreSQL_select_Query, [genero])
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/contenido_actores', methods=['GET'])
def get_contenido_by_estrella():
    estrella = request.headers.get('estrella')
    postgreSQL_select_Query = "SELECT c.nombre, c.link FROM contenido c JOIN actuan a on c.id " + "=" +" a.id_contenido JOIN estrellas e on a.id_estrella " + "=" + " e.id WHERE e.nombre ILIKE %s;"
    cursor.execute(postgreSQL_select_Query, [estrella])
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/contenido-premios', methods=['GET'])
def get_contenido_by_premios():
    premio = request.headers.get('premio')

    return get_contenido_premios(cursor, premio)

@app.route('/api/sugerencias', methods=['GET'])
def get_sugrencias():
    premio = request.headers.get('id')
    return get_contenido_sugerido(cursor, premio)


@app.route('/api/verdenuevo', methods=['GET'])
def get_verdenuevo():
    perfil = request.headers.get('id')
    postgreSQL_select_Query = "SELECT contenido.nombre, contenido.link, contenido.imagen FROM visto JOIN contenido ON visto.id_contenido = contenido.id WHERE visto.id_perfil = %s AND terminado=true;"
    cursor.execute(postgreSQL_select_Query, [perfil])
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1], "imagen":elements[2]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/randomcontenido', methods=['GET'])
def get_random():
    query = "SELECT nombre, link, imagen FROM contenido ORDER BY random() limit 1"
    cursor.execute(query)
    random = cursor.fetchall()
    response = {'nombre': random[0][0], 'link' : random[0][1], "imagen":random[0][2]}
    return jsonify(response)

@app.route('/api/seguirviendo', methods=['GET'])
def get_seguirviendo():
    perfil = request.headers.get('id')
    postgreSQL_select_Query = "SELECT contenido.nombre, contenido.link, contenido.imagen FROM visto JOIN contenido ON visto.id_contenido = contenido.id WHERE visto.id_perfil = %s AND terminado=false;"
    cursor.execute(postgreSQL_select_Query, [perfil])
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1], "imagen":elements[2]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/all-contenido', methods=['GET'])
def get_allContent():
    postgreSQL_select_Query = "SELECT nombre, link, imagen FROM contenido"
    cursor.execute(postgreSQL_select_Query)
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1], "imagen":elements[2]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/favoritos', methods=['GET'])
def get_favorites():
    perfil = request.headers.get('id')
    query = "SELECT c.nombre, c.link, c.imagen FROM contenido c JOIN favoritos f ON c.id = f.id_contenido WHERE id_perfil = %s;"
    cursor.execute(query, [perfil])
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1], "imagen":elements[2]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/favoritos', methods=['POST'])
def agregar_favoritos():
    content = request.json
    query = "SELECT id FROM contenido WHERE nombre = %s;"
    cursor.execute(query, [content['nombre']])
    contenido = cursor.fetchall()
    contenido = contenido[0][0]
    query1 = "insert into favoritos values(%s, %s);"
    cursor.execute(query1, [content['idperfil'],contenido])
    connection.commit()
    response = {"message": "success"}
    return jsonify(response)

@app.route('/api/favoritos', methods=['DELETE'])
def delete_favoritos():
    content = request.json
    query = "SELECT id FROM contenido WHERE nombre = %s;"
    cursor.execute(query, [content['nombre']])
    contenido = cursor.fetchall()
    contenido = contenido[0][0]
    query1 = "DELETE FROM favoritos WHERE id_perfil = %s AND id_contenido = %s;"
    cursor.execute(query1, [content['idperfil'],contenido])
    connection.commit()
    response = {"message": "success"}
    return jsonify(response)

@app.route('/api/consumo', methods=['POST'])
def modify_consumo():
    id = request.headers.get('id')
    nombre = request.headers.get('contenido')
    query = "SELECT id FROM contenido WHERE nombre = %s;"
    cursor.execute(query, [nombre])
    contenido = cursor.fetchall()
    id_contenido = contenido[0][0]

    time = datetime.now()

    query1 = "INSERT INTO consumo values(%s, %s, %s);"
    cursor.execute(query1, [id, id_contenido, time])
    connection.commit()
    response = {"message": "success"}
    return jsonify(response)

@app.route('/api/pelicula', methods=['POST'])
def agregar_visto():
    content = request.json
    cursor = connection.cursor()
    query = "SELECT id FROM contenido WHERE nombre = %s;"
    cursor.execute(query, [content['nombre']])
    data = cursor.fetchall()
    query2 = "SELECT * FROM visto WHERE id_contenido = %s AND id_perfil = %s;"
    cursor.execute(query2, [data[0][0], content['id']])
    datos = cursor.fetchall()
    if(datos):
        query3 = "UPDATE visto SET terminado = false WHERE id_contenido = %s AND id_perfil = %s;"
        cursor.execute(query3, [data[0][0], content['id']])
        connection.commit()
    else:
        query4 = "INSERT INTO visto VALUES (%s, %s, false);"
        cursor.execute(query4, [content['id'], data[0][0]])
        connection.commit()
    return jsonify({'message': 'success'})

@app.route('/api/pelicula', methods=['PUT'])
def modify_visto():
    content = request.json
    cursor = connection.cursor()
    query = "SELECT id FROM contenido WHERE nombre = %s;"
    cursor.execute(query, [content['nombre']])
    data = cursor.fetchall()
    query = "update visto set terminado=true where id_perfil=%s and id_contenido=%s;"
    cursor.execute(query, [content['id'],data[0][0]])
    return jsonify({'message': 'success'})

@app.route('/api/ajustecuenta', methods=['GET'])
def ajustar_cuenta():
    correo = request.headers.get("correo")
    query = "SELECT tipo_cuenta FROM cuenta WHERE correo= %s;"
    cursor.execute(query, [correo])
    tipo = cursor.fetchall()
    response = {"tipo": tipo[0][0]}
    return jsonify(response)

@app.route('/api/ajustecuenta', methods=['PUT'])
def actualizar_cuenta():
    content = request.json
    datos = []
    for keys in content:
        datos.append(content[keys])
    print(datos)
    query = "UPDATE cuenta SET tipo_cuenta=%s, administrador =%s, accion = 'update' WHERE correo=%s;"
    cursor.execute(query, [datos[0], datos[1], datos[1]])
    connection.commit()
    cant = 0
    if datos[0] == 'basica' :
        cant = 1
    elif datos[0] == 'estandar' :
        cant =4 
    elif datos[0] == 'avanzada' :
        cant =8 

    query = """select id from perfiles where correo_cuenta = %s and cast(right(id, 1) as integer) <= %s order by cast(right(id, 1) as integer) asc""" 
    cursor.execute(query, [datos[1], cant])
    data = cursor.fetchall()
    stored = []
    for elementos in data:
        stored.append(elementos[0])
    
    for elementos in stored:
        query = "update perfiles set activo=true, cuenta=%s, accion='update' where id=%s"
        cursor.execute(query, [datos[1], elementos])

    query = """select id from perfiles where correo_cuenta = %s and cast(right(id, 1) as integer) > %s order by cast(right(id, 1) as integer) asc""" 
    cursor.execute(query, [datos[1], cant])
    data = cursor.fetchall()
    stored = []
    for elementos in data:
        stored.append(elementos[0])
    
    for elementos in stored:
        query = "update perfiles set activo=false, cuenta=%s, accion='update' where id=%s"
        cursor.execute(query, [datos[1], elementos])
    connection.commit()

    response = {"message": "success"}
    return jsonify(response)

@app.route('/api/anuncio', methods=['GET'])
def get_anuncio():
    postgreSQL_select_Query = "SELECT id, link FROM anuncios order by random() limit 1; "
    cursor.execute(postgreSQL_select_Query)
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'id': elements[0], 'link' : elements[1]}
        response.append(new_obj)
    
    nombre = request.headers.get('nombre')
    query = "SELECT id FROM contenido WHERE nombre = %s;"
    cursor.execute(query, [nombre])
    contenido = cursor.fetchall()
    id_contenido = contenido[0][0]


    time = datetime.now()
    query1 = "INSERT INTO regis_anun values(%s, %s, %s);"
    cursor.execute(query1, [id_contenido, response[0]['id'], time])
    connection.commit()

    return jsonify({'link': response[0]['link']})

@app.route('/api/admin_getCuenta', methods=['GET'])
def admin_GetCuenta():
    
    return admin_getCuenta(cursor)

@app.route('/api/admin_Activado', methods=['PUT'])
def admin_Activado():
    content = request.json

    return admin_activado(cursor, content, connection)

@app.route('/api/admin_getEstrellas', methods=['GET'])
def admin_GetEstrellas():
    return admin_getestrellas(cursor)


@app.route('/api/admin_getAnunciantes', methods=['GET'])
def admin_GetAnunciantes():
    return admin_getanunciantes(cursor)


@app.route('/api/admin_getAnuncios', methods=['GET'])
def admin_GetAnuncios():
    return admin_getanuncios(cursor)

@app.route('/api/admin_getCont', methods=['GET'])
def admin_GetCont():
    return admin_getcont(cursor)

@app.route('/api/stars', methods=['PUT'])
def admin_edistar():
    content = request.json
    return edit_star(connection, cursor, content)

@app.route('/api/anuncios', methods=['PUT'])
def change_anun():
    content = request.json
    return change_anunciante(connection, cursor, content)

@app.route('/api/anuncios', methods=['DELETE'])
def delete_anun():
    content = request.headers.get('id')
    admin = request.headers.get('administrador')
    return delete_anuncios(admin, content)

@app.route('/api/cuentas', methods=['PUT'])
def change_corre():
    content = request.json
    return change_correo(connection, cursor, content)

@app.route('/api/anunciante', methods=['PUT'])
def change_nunciante():
    content = request.json
    return change_anunciante2(connection, cursor, content)

@app.route('/api/anunciante', methods=['DELETE'])
def delete_nunciante():
    nombre = request.headers.get('nombre')
    admin = request.headers.get('administrador')
    print(nombre)
    return delete_anunciante(admin, nombre)

@app.route('/api/premios', methods=['GET'])
def get_Premios():
    return get_premios(cursor)

@app.route('/api/movie', methods=['POST'])
def create_Film():
    content = request.json
    return crear_pelicula(connection, cursor, content)

@app.route('/api/contenido', methods=['DELETE'])
def delete_ontenido():
    nombre = request.headers.get('nombre')
    administrador = request.headers.get('administrador')
    return delete_contenido(connection, cursor, nombre, administrador)

@app.route('/api/anunciantes', methods=['POST'])
def create_ANUNCIANTE():
    content = request.json
    return crear_anunciante(connection, cursor, content)

@app.route('/api/anuncio', methods=['POST'])
def create_ANUNCIo():
    content = request.json
    return crear_anuncio(connection, cursor, content)

@app.route('/api/editPelis', methods=['GET'])
def get_todito():
    nombre = request.headers.get('nombre')
    return get_todopeli(nombre, cursor)

@app.route('/api/editPelis', methods=['PUT'])
def update_todito():
    content = request.json
    return update_peli(cursor, connection, content)

@app.route('/api/Top10gen', methods=['GET'])
def get10gen():
    fechaI = request.headers.get('fechaI')
    fechaF = request.headers.get('fechaF')


    return get_10gen(fechaI, fechaF, cursor)

@app.route('/api/Reprod', methods=['GET'])
def getReprod():
    cuenta = request.headers.get('cuenta')
    fechaI = request.headers.get('fechaI')
    fechaF = request.headers.get('fechaF')


    return get_Reprod(fechaI, fechaF, cuenta, cursor)

@app.route('/api/Directo', methods=['GET'])
def getDirecto():

    return get_Directo(cursor)

@app.route('/api/Acto', methods=['GET'])
def getActo():

    return get_Acto(cursor)

@app.route('/api/Cant', methods=['GET'])
def getCant():

    return get_Cant(cursor)

@app.route('/api/pico', methods=['GET'])
def getPico():
    fechaI = request.headers.get('fechaI')
    return get_hora(cursor, fechaI)

@app.route('/api/newAdmin', methods=['POST'])
def insertAdmin():
    content = request.json
    return crear_admin(cursor, content, connection)

@app.route('/api/simulacion', methods=['POST'])
def simulation():
    content = request.json

    return ejecutar_simulacion(cursor, connection, content['fecha'], content['cantidad'])

@app.route('/api/busqueda', methods=['POST'])
def busqueda():
    content = request.json['busqueda']
    query = "INSERT INTO termino_busqueda values (%s)"
    cursor.execute(query, [content])
    connection.commit()
    return jsonify({"message":"success"})

@app.route('/api/busqueda', methods=['GET'])
def busqueda_terminos():
    query = "select * from top_terminos"
    cursor.execute(query)
    terminos = cursor.fetchall()
    response = []
    for elements in terminos:
        new_obj = {'termino': elements[0], 'count': elements[1]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/top_5_admin', methods=['GET'])
def admins():
    fechaI = request.headers.get('fechaI')
    fechaF = request.headers.get('fechaF')
    query = "SELECT * FROM top_admin(%s, %s)"
    cursor.execute(query, [fechaI, fechaF])
    admins = cursor.fetchall()
    response = []
    for elements in admins:
        new_obj = {'nombre': elements[0]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/sinTerminar', methods=['GET'])
def top_sin_terminar():
    fechaI = request.headers.get('fechaI')
    fechaF = request.headers.get('fechaF')
    query = "SELECT * FROM sinterminar(%s, %s)"
    cursor.execute(query, [fechaI, fechaF])
    admins = cursor.fetchall()
    response = []
    for elements in admins:
        new_obj = {'nombre': elements[0]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/Pormes', methods=['GET'])
def top_por_mes():
    mes = request.headers.get('mes')
    print(mes)
    query = "SELECT * FROM top5(%s)"
    cursor.execute(query, [mes])
    admins = cursor.fetchall()
    response = []
    for elements in admins:
        new_obj = {'hora': elements[0], 'nombre': elements[1]}
        response.append(new_obj)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)