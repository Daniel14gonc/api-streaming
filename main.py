from random import random
from flask import Flask, request, json
from flask_cors import CORS, cross_origin
from flask import jsonify
from config import config
import psycopg2
from perfiles import *
from contenido_premios import *
from contenido_sugerido import *
from admin import *
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
    postgreSQL_select_Query = "SELECT passw FROM cuenta WHERE correo='%s' and activo = true"%(correo)
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

    megaQuery = f'''select nombre, link, imagen from contenido where nombre ILIKE '%{nombre}%'
                    union
                    SELECT distinct(c.nombre), c.link, c.imagen FROM contenido c JOIN pertenece p on c.id = p.id_contenido WHERE p.nombre_genero ILIKE '%{nombre}%'
                    union
                    SELECT distinct(c.nombre), c.link, c.imagen FROM contenido c JOIN actuan a on c.id = a.id_contenido JOIN estrellas e on a.id_estrella = e.id WHERE e.nombre ILIKE '%{nombre}%'
                    union
                    select distinct(c.nombre), c.link, c.imagen from premiacion p join contenido c on c.id = p.id_contenido where p.nombre_premio ILIKE '%{nombre}%' 
                    union
                    select nombre, link, imagen from contenido where cast(fecha_estreno as varchar) like '%{nombre}%'
                    union
                    select distinct(p.nombre), p.link, p.imagen from director d join contenido p on d.id=p.id_director 
                    where d.nombre ilike '%{nombre}%';

    '''

    cursor.execute(megaQuery)
    contenido = cursor.fetchall()
    response = []
    for elements in contenido:
        new_obj = {'nombre': elements[0], 'link' : elements[1], "imagen":elements[2]}
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
    content = request.json
    cursor = connection.cursor()
    query = "SELECT id FROM contenido WHERE nombre = '%s'"%(content['nombre'])
    cursor.execute(query)
    data = cursor.fetchall()
    query = "update visto set terminado=true where id_perfil='%s' and id_contenido='%s';"%(content['id'],data[0][0])
    cursor.execute(query)
    return jsonify({'message': 'success'})

@app.route('/api/ajustecuenta', methods=['GET'])
def ajustar_cuenta():
    correo = request.headers.get("correo")
    query = "SELECT tipo_cuenta FROM cuenta WHERE correo='%s';"%correo
    print(query)
    cursor.execute(query)
    tipo = cursor.fetchall()
    response = {"tipo": tipo[0][0]}
    return jsonify(response)

@app.route('/api/ajustecuenta', methods=['PUT'])
def actualizar_cuenta():
    content = request.json
    datos = []
    for keys in content:
        datos.append(content[keys])
    query = "UPDATE cuenta SET tipo_cuenta='%s' WHERE correo='%s'"%(datos[0], datos[1])
    cursor.execute(query)
    connection.commit()
    cant = 0
    if datos[0] == 'basica' :
        cant = 1
    elif datos[0] == 'estandar' :
        cant =4 
    elif datos[0] == 'avanzada' :
        cant =8 

    query = f"""select id from perfiles where correo_cuenta = '{datos[1]}' and cast(right(id, 1) as integer) <= {cant} order by cast(right(id, 1) as integer) asc""" 
    cursor.execute(query)
    data = cursor.fetchall()
    stored = []
    for elementos in data:
        stored.append(elementos[0])
    
    for elementos in stored:
        query = f"update perfiles set activo=true where id='{elementos}'"
        cursor.execute(query)

    query = f"""select id from perfiles where correo_cuenta = '{datos[1]}' and cast(right(id, 1) as integer) > {cant} order by cast(right(id, 1) as integer) asc""" 
    cursor.execute(query)
    data = cursor.fetchall()
    stored = []
    for elementos in data:
        stored.append(elementos[0])
    
    for elementos in stored:
        query = f"update perfiles set activo=false where id='{elementos}'"
        cursor.execute(query)
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
    query = "SELECT id FROM contenido WHERE nombre = '%s'"%(nombre)
    cursor.execute(query)
    contenido = cursor.fetchall()
    id_contenido = contenido[0][0]


    time = datetime.now()
    query1 = "INSERT INTO regis_anun values('%s', '%s', '%s')"%(id_contenido, response[0]['id'], time)
    cursor.execute(query1)
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
    return delete_anuncios(connection, cursor, content)

if __name__ == '__main__':
    app.run(debug=True)