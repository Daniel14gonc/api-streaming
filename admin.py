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
    query1 = "select activo from cuenta where correo=%s;"
    cursor.execute(query1, [content['correo']])
    valor = cursor.fetchall()
    if(valor[0][0]==True):
        query = "update cuenta set activo = false where correo=%s;"
        cursor.execute(query, [content['correo']])
    else:
        query = "update cuenta set activo = true where correo=%s;"
        cursor.execute(query, [content['correo']])
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
    query = "UPDATE estrellas SET nombre = %s where id=%s;"
    cursor.execute(query, [content['nombre'], content['id']])
    connection.commit()
    
    return jsonify({'message': 'success'})


def change_anunciante(connection, cursor, content):
    query = "SELECT id FROM anunciante where nombre = %s;"
    cursor.execute(query, [content['anunciante']])
    datos = cursor.fetchall()
    ida = datos[0][0]

    query = "UPDATE anuncios set id_anunciante = %s where id=%s"
    cursor.execute(query, [ida, content['id']])
    connection.commit()

    return jsonify({'message': 'success'})

def delete_anuncios(connection, cursor, id):

    query = "DELETE FROM anuncios WHERE id = %s;"
    cursor.execute(query, [id])
    connection.commit()

    return jsonify({'message': 'success'})

def change_correo(connection, cursor, content):
    print(content)
    query = "UPDATE cuenta set correo = %s where correo=%s;"
    cursor.execute(query, [content['new'], content['old']])
    connection.commit()

    return jsonify({'message': 'success'})

def change_anunciante2(connection, cursor, content):
    query = "UPDATE anunciante set nombre = %s where nombre=%s;"
    cursor.execute(query, [content['new'], content['old']])
    connection.commit()

    return jsonify({'message': 'success'})

def delete_anunciante(connection, cursor, nombre):
    query = "DELETE FROM anunciante WHERE nombre = %s;"
    print(query, [nombre])
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
  
  
    query = "SELECT id FROM director WHERE nombre=%s;"
    cursor.execute(query, [list[2]])
    id_d = cursor.fetchall()[0][0]
    
    query = "SELECT id FROM contenido order by id desc limit 1;"
    cursor.execute(query)
    id = int(cursor.fetchall()[0][0]) + 1
    
    query = "INSERT INTO contenido VALUES (%s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(query, [id, list[0], list[1], id_d, list[3], list[4], list[5]])
    connection.commit()

    for elements in list[6]:
        query = "SELECT id FROM estrellas WHERE nombre=%s;"
        cursor.execute(query, [elements])
        id_e = cursor.fetchall()[0][0]
        
        query = "INSERT INTO actuan VALUES (%s , %s);"
        cursor.execute(query, [id, id_e])
        connection.commit()

    return jsonify({'message':'success'})

def delete_contenido(connection, cursor, nombre):
    query = "DELETE FROM contenido WHERE nombre = %s;"
    cursor.execute(query, [nombre])
    connection.commit()

    return jsonify({'message': 'success'})


def crear_anunciante(connection, cursor, content):
    content = content['data']


    query = "SELECT id FROM anunciante order by id desc limit 1;"
    cursor.execute(query)
    id = int(cursor.fetchall()[0][0]) + 1
  
    query = "insert into anunciante values (%s, %s);"
    cursor.execute(query, [id,content])

    connection.commit()

    return jsonify({'message':'success'})

def crear_anuncio(connection, cursor, content):
    link = content['link']
    anunciante = content['anunciante']

    query = "SELECT id FROM anunciante where nombre=%s;"
    cursor.execute(query, [anunciante])
    id_anun = cursor.fetchall()[0][0]

    query = "SELECT id FROM anuncios order by id desc limit 1;"
    cursor.execute(query)
    id = int(cursor.fetchall()[0][0]) + 1

    if(id<10):
        id="0"+str(id)
  
    query = "insert into anuncios values (%s , %s, %s);"
    cursor.execute(query, [id,id_anun, link])

    connection.commit()

    return jsonify({'message':'success'})

def get_todopeli(nombre, cursor):
    query = "select d.nombre , c.duracion, c.link, c.imagen from contenido c join director d on d.id=c.id_director where c.nombre=%s;"
    cursor.execute(query, [nombre])
    elements = cursor.fetchall()
    response = {'nombre': elements[0][0], 'duracion' : elements[0][1],'link' : elements[0][2],'imagen' : elements[0][3]}
    return jsonify(response)

def update_peli(cursor, connection, content):
    content = content['data']

    query1 = "SELECT id FROM director WHERE nombre = %s"
    cursor.execute(query1, [content[1]])
    id = cursor.fetchall()[0][0]

    query = "UPDATE contenido SET nombre = %s, id_director = %s, duracion = %s, link = %s, imagen = %s WHERE nombre = %s;"
    cursor.execute(query, [content[0], id, content[2], content[3], content[4], content[5]])
    connection.commit()

    return jsonify({"message":"success"})

def get_10gen(fechaI, fechaF, cursor):
    query="""select p.nombre_genero, sum(c2.duracion)
    from consumo c
    join  contenido c2 on c.id_contenido = c2.id
    join pertenece p on p.id_contenido = c2.id
    where c.fecha_visualizacion>=%s and c.fecha_visualizacion<=%s
    group by p.nombre_genero
    order by sum(c2.duracion) desc  limit 10;"""

    cursor.execute(query, [fechaI, fechaF])
    generos = cursor.fetchall()
    response=[]
    for elements in generos:
        obj = {'genero': elements[0], 'conteo' : elements[1]}
        response.append(obj)

    return jsonify(response)

def get_Reprod(fechaI, fechaF, cuenta, cursor):
    query="""
    select p.nombre_genero, count(*) from consumo c join pertenece p on c.id_contenido = p.id_contenido
    join perfiles p2 on c.id_perfil = p2.id join cuenta c2 on c2.correo = p2.correo_cuenta
    where c2.tipo_cuenta = %s and
    c.fecha_visualizacion>=%s and c.fecha_visualizacion<=%s
    group by p.nombre_genero;
    """

    cursor.execute(query, [cuenta, fechaI, fechaF])
    cuentas = cursor.fetchall()
    response=[]
    for elements in cuentas:
        obj = {'cuenta': elements[0], 'conteo' : elements[1]}
        response.append(obj)

    return jsonify(response)

def get_Directo(cursor):
    query="""
        select distinct(director) from (
        select c2.id, c2.nombre, d.nombre as director, count(*) from visto v join perfiles p on v.id_perfil = p.id 
        join cuenta c on c.correo = p.correo_cuenta
        join contenido c2 on v.id_contenido = c2.id
        join director d on d.id = c2.id_director 
        where c.tipo_cuenta != 'basica' group by c2.id, d.nombre order by count(*) desc limit 10) as tabla;
    """
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response=[]
    for elements in cuentas:
        obj = {'nombre': elements[0]}
        response.append(obj)

    return jsonify(response)

def get_Acto(cursor):
    query="""
        select distinct(e.nombre) from actuan a join estrellas e on e.id = a.id_estrella  where a.id_contenido in (
            select id from (
                select v.id_contenido as id, count(*) from visto v join perfiles p on v.id_perfil = p.id 
                join cuenta c on c.correo = p.correo_cuenta
                where c.tipo_cuenta != 'basica' group by v.id_contenido order by count(*) desc limit 10
            ) as top
        );
    """
    cursor.execute(query)
    cuentas = cursor.fetchall()
    response=[]
    for elements in cuentas:
        obj = {'nombre': elements[0]}
        response.append(obj)

    return jsonify(response)

def get_Cant(cursor):
    query="""
    select count(*) from cuenta where fecha_creacion >= to_char(CURRENT_DATE - INTERVAL '6 months', 'YYYY-MM-01')::date
    and tipo_cuenta = 'avanzada';
    """
    cursor.execute(query)
    cant = cursor.fetchall()[0][0]

    return jsonify(cant)


def get_hora(cursor, fecha):
    fecha1 = fecha + ' 23:59:59.999'
    
    query=f"""
        select hora from (
            select extract(hour from c.fecha_visualizacion) as hora, count(*)  from consumo c 
            where c.fecha_visualizacion between %s and %s
            group by extract(hour from c.fecha_visualizacion) order by count(*) desc limit 1) as tabla;
    """
    cursor.execute(query, [fecha, fecha1])
    cant = cursor.fetchall()[0][0]

    return jsonify({'hora' : cant})


