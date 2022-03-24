from flask import jsonify

def crear_perfil(connection, cursor, content):

    postgreSQL_select_Query = "SELECT correo FROM cuenta WHERE correo='%s'"%(content['correo'])
    cursor.execute(postgreSQL_select_Query)
    data = cursor.fetchall()
    if (data):
        tipo = get_cuenta(cursor, content['correo'])
        conteo = get_count(cursor, content['correo'])
        if tipo == 'basica':
            if conteo < 1:
                id = content['correo'] + str(conteo + 1)
                datos = (id, content['nombre'], content['correo'])
                commit(connection, cursor, datos)
                response = { "success" : "Perfil añadido"}
            else:
                response = {"error" : "Ya llegaste al limite de perfiles"}
        if tipo == 'estandar':
            if conteo < 4:
                id = content['correo'] + str(conteo + 1)
                datos = (id, content['nombre'], content['correo'])
                commit(connection, cursor, datos)
                response = { "success" : "Perfil añadido"}
            else:
                response = {"error" : "Ya llegaste al limite de perfiles"}
        if tipo == 'avanzada':
            if conteo < 8:
                id = content['correo'] + str(conteo + 1)
                datos = (id, content['nombre'], content['correo'])
                commit(connection, cursor, datos) 
                response = { "success" : "Perfil añadido"}
            else:
                response = {"error" : "Ya llegaste al limite de perfiles"}
    else:
        response = {'error': 'correo no existente'}

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