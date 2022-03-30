from flask import Flask, request, json
from flask_cors import CORS, cross_origin
from flask import jsonify
from config import config
import psycopg2
from perfiles import *
from contenido_premios import *
from contenido_sugerido import *

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

    
if __name__ == '__main__':
    app.run(debug=True)