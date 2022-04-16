from flask import jsonify


def get_contenido_sugerido(cursor, id):
    
    query = '''
            select distinct(c1.nombre), c1.link, c1.imagen from contenido c1 join pertenece p1 on c1.id = p1.id_contenido
            where p1.nombre_genero in (
                select p.nombre_genero from pertenece p where p.id_contenido in (
                select v.id_contenido from visto v where v.id_perfil = %s
            )) 
            and c1.id not in (select id_contenido from visto where id_perfil = %s)
            union
            select distinct(c1.nombre), c1.link, c1.imagen from contenido c1 join actuan a1 on c1.id = a1.id_contenido
            where a1.id_estrella in (
                select e.id from actuan a join estrellas e on a.id_estrella = e.id where a.id_contenido in (
                select v.id_contenido from visto v where v.id_perfil = %s
            )) 
            and c1.id not in (select id_contenido from visto where id_perfil = %s);'''
    cursor.execute(query, [id, id, id, id])
    data = cursor.fetchall()
    response = []
    if data:
        for elements in data:
            new_obj = {'nombre':elements[0], "link": elements[1], "imagen":elements[2]}
            response.append(new_obj)
    else:
        query = 'select nombre, link, imagen from contenido;'
        cursor.execute(query)
        data = cursor.fetchall()
        for elements in data:
            new_obj = {'nombre':elements[0], "link": elements[1], "imagen":elements[2]}
            response.append(new_obj)
            
    return jsonify(response)