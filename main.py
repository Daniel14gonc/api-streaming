from random import random
from flask import Flask, request, json
from flask_cors import CORS, cross_origin
from flask import jsonify
from config import config
import psycopg2
from perfiles import *
from contenido_premios import *
from contenido_sugerido import *
from datetime import datetime

connection = psycopg2.connect(user="postgres",
                                  password="ketchup14",
                                  host="streaming.cddkmwmgfell.us-east-1.rds.amazonaws.com",
                                  port="5432",
                                  database="Streaming")

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
    sql = "INSERT INTO director VALUES('%s', '%s')"
    cursor.execute(sql%tuple(lista))
    connection.commit()
    response = {'message': 'success 200'}
    return jsonify(response)

@app.route('/api/signin', methods=['GET'])
def signin():
    correo = request.headers.get('correo')
    password = request.headers.get('password')
    postgreSQL_select_Query = "SELECT passw FROM cuenta WHERE correo='%s'"%(correo)
    cursor.execute(postgreSQL_select_Query)
    data = cursor.fetchall()
    response = {'message' : 'error 401'}
    if data:
        passw = data[0][0]
        if(passw==password):
            response = {'message': 'success 200'}
        else:
            response = {'message' : 'error 409'}

    return jsonify(response)

@app.route('/api/logon', methods=['POST'])
def logon():
    content = request.json
    datos = []
    for keys in content:
        datos.append(content[keys])
    postgreSQL_select_Query = "SELECT correo FROM cuenta WHERE correo='%s'"%(content['correo'])
    cursor.execute(postgreSQL_select_Query)
    data = cursor.fetchall()
    if (not data):
        sql = "insert into cuenta values ('%s', '%s', '%s', true, current_timestamp);"
        cursor.execute(sql%tuple(datos))
        connection.commit()
        response = {'message': 'success'}
    else:
        response = {'message': 'error 409'}

    return jsonify(response)

@app.route('/api/signinAdmin', methods=['GET'])
def signinAdmin():
    correo = request.headers.get('correo')
    password = request.headers.get('password')
    postgreSQL_select_Query = "SELECT passw FROM administrador WHERE correo='%s'"%(correo)
    cursor.execute(postgreSQL_select_Query)
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
    postgreSQL_select_Query = "SELECT correo FROM administrador WHERE correo='%s'"%(content['correo'])
    cursor.execute(postgreSQL_select_Query)
    data = cursor.fetchall()
    if (not data):
        sql = "insert into administrador values ('%s', '%s');"
        cursor.execute(sql%tuple(datos))
        connection.commit()
        response = {'message': 'success'}
    else:
        response = {'message': 'error 409'}

    return jsonify(response)

@app.route('/api/perfiles', methods=['POST'])
def add_perfiles():
    content = request.json
    
    return crear_perfil(connection, cursor, content)

@app.route('/api/perfiles', methods=['GET'])
def get_perfiles():
    content = request.headers.get('correo')
    
    return get_profiles(cursor, content)

@app.route('/api/perfiles', methods=['PUT'])
def update_perfiles():
    content = request.json
    
    return actualizar_perfil(cursor, content, connection)

@app.route('/api/contenido', methods=['GET'])
def get_contenido():
    nombre = request.headers.get('nombre')
    postgreSQL_select_Query = "select * from contenido where nombre ILIKE '%s';"%(nombre)
    cursor.execute(postgreSQL_select_Query)
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'id': elements[0], 'nombre': elements[1], 'fecha_estreno': elements[2], 'id_director': elements[3], 'duracion': elements[4], 'link': elements[5]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/contenido_generos', methods=['GET'])
def get_contenido_by_genero():
    genero = request.headers.get('genero')
    postgreSQL_select_Query = "SELECT c.nombre, c.link FROM contenido c JOIN pertenece p on c.id " + "=" +" p.id_contenido WHERE p.nombre_genero ILIKE '%s';"%(genero)
    cursor.execute(postgreSQL_select_Query)
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/contenido_actores', methods=['GET'])
def get_contenido_by_estrella():
    estrella = request.headers.get('estrella')
    postgreSQL_select_Query = "SELECT c.nombre, c.link FROM contenido c JOIN actuan a on c.id " + "=" +" a.id_contenido JOIN estrellas e on a.id_estrella " + "=" + " e.id WHERE e.nombre ILIKE '%s';"%(estrella)
    cursor.execute(postgreSQL_select_Query)
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
    postgreSQL_select_Query = "SELECT contenido.nombre, contenido.link, contenido.imagen FROM visto JOIN contenido ON visto.id_contenido = contenido.id WHERE visto.id_perfil = '%s' AND terminado=true"%(perfil)
    cursor.execute(postgreSQL_select_Query)
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
    postgreSQL_select_Query = "SELECT contenido.nombre, contenido.link, contenido.imagen FROM visto JOIN contenido ON visto.id_contenido = contenido.id WHERE visto.id_perfil = '%s' AND terminado=false"%(perfil)
    cursor.execute(postgreSQL_select_Query)
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
    query = "SELECT c.nombre, c.link, c.imagen FROM contenido c JOIN favoritos f ON c.id = f.id_contenido WHERE id_perfil = '%s';"
    cursor.execute(query%perfil)
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1], "imagen":elements[2]}
        response.append(new_obj)
    return jsonify(response)

@app.route('/api/favoritos', methods=['POST'])
def agregar_favoritos():
    content = request.json
    query = "SELECT id FROM contenido WHERE nombre = '%s'"%(content['nombre'])
    cursor.execute(query)
    contenido = cursor.fetchall()
    contenido = contenido[0][0]
    query1 = "insert into favoritos values('%s', '%s')"%(content['idperfil'],contenido)
    cursor.execute(query1)
    connection.commit()
    response = {"message": "success"}
    return jsonify(response)

@app.route('/api/favoritos', methods=['DELETE'])
def delete_favoritos():
    content = request.json
    query = "SELECT id FROM contenido WHERE nombre = '%s'"%(content['nombre'])
    cursor.execute(query)
    contenido = cursor.fetchall()
    contenido = contenido[0][0]
    query1 = "DELETE FROM favoritos WHERE id_perfil = '%s' AND id_contenido = '%s'"%(content['idperfil'],contenido)
    cursor.execute(query1)
    connection.commit()
    response = {"message": "success"}
    return jsonify(response)

@app.route('/api/consumo', methods=['POST'])
def modify_consumo():
    id = request.headers.get('id')
    nombre = request.headers.get('contenido')

    query = "SELECT id FROM contenido WHERE nombre = '%s'"%(nombre)
    cursor.execute(query)
    contenido = cursor.fetchall()
    id_contenido = contenido[0][0]

    time = datetime.now()

    query1 = "INSERT INTO consumo values('%s', '%s', '%s')"%(id, id_contenido, time)
    cursor.execute(query1)
    connection.commit()
    response = {"message": "success"}
    return jsonify(response)

@app.route('/api/pelicula', methods=['POST'])
def agregar_visto():
    content = request.json
    print(content)
    cursor = connection.cursor()
    query = "SELECT id FROM contenido WHERE nombre = '%s'"%(content['nombre'])
    cursor.execute(query)
    data = cursor.fetchall()
    query2 = "SELECT * FROM visto WHERE id_contenido = '%s' AND id_perfil = '%s'"%(data[0][0], content['id'])
    cursor.execute(query2)
    datos = cursor.fetchall()
    if(datos):
        query3 = "UPDATE visto SET terminado = false WHERE id_contenido = '%s' AND id_perfil = '%s'"%(data[0][0], content['id'])
        cursor.execute(query3)
        connection.commit()
    else:
        query4 = "INSERT INTO visto VALUES ('%s', '%s', false)"%(content['id'], data[0][0])
        cursor.execute(query4)
        connection.commit()
    return jsonify({'message': 'success'})

@app.route('/api/pelicula', methods=['PUT'])
def modify_visto():
    id = request.headers.get('id')
    nombre = request.headers.get('nombre')

    query = "SELECT id FROM contenido WHERE nombre = '%'"%nombre
    cursor.execute(query)
    id_conteido = cursor.fetchall()


if __name__ == '__main__':
    app.run(debug=True)