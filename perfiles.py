from urllib import response
from flask import jsonify

def crear_perfil(connection, cursor, content):

    postgreSQL_select_Query = "SELECT correo FROM cuenta WHERE correo='%s'"%(content['correo'])
    cursor.execute(postgreSQL_select_Query)
    data = cursor.fetchall()
    if (data):
        query = "select nombre from perfiles where nombre='%s' and correo_cuenta ='%s';"%(content['nombre'], content['correo'])
        cursor.execute(query)
        datas = cursor.fetchall()
        if(datas):
            response = {'message': 'Error: Un perfil con ese nombre ya existe.'}
            return jsonify(response)
        tipo = get_cuenta(cursor, content['correo'])
        conteo = get_count(cursor, content['correo'])
        if tipo == 'basica':
            if conteo < 1:
                id = content['correo'] + str(conteo + 1)
                datos = (id, content['nombre'], content['correo'])
                commit(connection, cursor, datos)
                response = { "message" : "Perfil añadido"}
            else:
                response = {"message" : "Error: Ya llegaste al limite de perfiles."}
        if tipo == 'estandar':
            if conteo < 4:
                id = content['correo'] + str(conteo + 1)
                datos = (id, content['nombre'], content['correo'])
                commit(connection, cursor, datos)
                response = { "message" : "Perfil añadido"}
            else:
                response = {"message" : "Error: Ya llegaste al limite de perfiles,"}
        if tipo == 'avanzada':
            if conteo < 8:
                id = content['correo'] + str(conteo + 1)
                datos = (id, content['nombre'], content['correo'])
                commit(connection, cursor, datos) 
                response = { "message" : "Perfil añadido"}
            else:
                response = {"message" : "Error: Ya llegaste al limite de perfiles."}
    else:
        response = {'message': 'Error: Correo no existente.'}

    return jsonify(response)


def get_profiles(cursor, correo):
    query = f"select id, nombre from perfiles where correo_cuenta = '{correo}' and activo = true"
    cursor.execute(query)
    data = cursor.fetchall()
    response = []
    if data:
        for elements in data:
            temp_obj = {"id_perfil" : elements[0], "nombre" : elements[1]}
            response.append(temp_obj)
    return jsonify(response)


def get_cuenta(cursor, correo):
    
    postgreSQL_select_Query = "SELECT tipo_cuenta FROM cuenta WHERE correo='%s'"%(correo)
    cursor.execute(postgreSQL_select_Query)
    data = cursor.fetchall()
    
    return data[0][0]

def get_count(cursor, correo):
    
    postgreSQL_select_Query = "select count(correo_cuenta) from perfiles where correo_cuenta = '%s'"%(correo)
    cursor.execute(postgreSQL_select_Query)
    conteo = cursor.fetchall()
    return int(conteo[0][0])

def commit(connection, cursor, data):
    sql = "insert into perfiles values ('%s', '%s', '%s', true, current_date)"
    cursor.execute(sql%data)
    connection.commit()

def actualizar_perfil(cursor, content, connection):
    if(content['dentro'] == 'false'):
        query = "UPDATE perfiles SET dentro = %s WHERE correo_cuenta = '%s' AND nombre = '%s'"%(content['dentro'], content['correo'], content['nombre'])
        cursor.execute(query)
        connection.commit()
        response = {"message": "success"}
        return jsonify(response)
    else:
        query2 = "SELECT dentro FROM perfiles WHERE correo_cuenta = '%s' AND dentro = true AND nombre = '%s'"%(content['correo'], content['nombre'])
        cursor.execute(query2)
        dentroo = cursor.fetchall()
        if(dentroo):
            response = {"message": "Error: Este perfil ya esta en uso."}
            return jsonify(response)
        else:
            query = "UPDATE perfiles SET dentro = %s WHERE correo_cuenta = '%s' AND nombre = '%s'"%(content['dentro'], content['correo'], content['nombre'])
            cursor.execute(query)
            connection.commit()
            response = {"message": "success"}
            return jsonify(response)