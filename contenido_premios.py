from flask import jsonify

def get_contenido_premios(cursor, premio):
    premio = '%' + premio + '%'
    query = f'''select distinct(c.nombre), c.link from premiacion p join contenido c on c.id = p.id_contenido
                where p.nombre_premio ILIKE %s '''
    cursor.execute(query, [premio])
    data = cursor.fetchall()
    if data:
        result = []
        for elements in data:
            temp_obj = {'nombre': elements[0], 'link': elements[1]}
            result.append(temp_obj)
        
        return jsonify(result)
    
    else:
        result = [{'Error 404': 'Contenido no encontrado'}]
        return jsonify(result)