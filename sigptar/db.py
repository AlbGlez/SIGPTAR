import mariadb
import itertools
from flask import current_app, g, json, jsonify
from .models.Usuario import Usuario
#from model import planta;

# DB access
def get_db():
    if 'db' not in g:      
        # connection for MariaDB
        g.db = mariadb.connect(**current_app.config['DBCONFIG'])
        # create a connection cursor
        #cur = conn.cursor()
        #g.db.row_factory = mariadb.Row
        #g.db.autocommit=True
    return g.db


def close_db(e=None):
    db=g.pop('db',None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)

# Data access
def get_plantas():
    cursor=get_db().cursor()
    cursor.execute('SELECT id_planta, nombre_ptar, e.nombre as estado, m.nombre as municipio,colonia, calle, numero, cp, '\
                    'coord_latitud, coord_longitud, superficie,caudal_entrada, influente_industrial, '\
                    'fecha_inicio_const,fecha_fin_const, fecha_inicio_oper, poblacion_beneficiada,anio_actual, '\
                    'tipo_tratamiento, gasto_diseño, gasto_operacion_estiaje,gasto_operacion_lluvia, ro_nombre_institucion, '\
                    'ro_nombre, ro_puesto,ro_correo, ro_telefono '\
                    'FROM planta p '\
                    'LEFT JOIN estado e on e.id_estado=p.estado_id '\
                    'LEFT JOIN municipio m on m.id_municipio=p.municipio_id')
    plantas=cursor.fetchall()    
    planta_col_names=[i[0] for i in cursor.description]
    print(planta_col_names)
    #Ojo: las etiquetas de las plantas estan en las tabla
    cursor.execute("SELECT campo,etiqueta,seccion FROM etiqueta where tabla='planta' order by orden")
    etiquetas = [row for row in cursor.fetchall() if row[0] in planta_col_names]
    # si las etiquetas regresan en formato de json objects
    #etiquetas=[dict((cursor.description[i][0], value) \
    #           for i, value in enumerate(row)) for row in cursor.fetchall()]
    print(etiquetas) 
    # únicamente se carga la info de las etiquetas que estén en los campos  
    #etiquetas=[reg for reg in etiq if reg[0] in planta_col_names]
    #print(etiquetas) 
    #etiquetas=[dictEtiq[key] for key in planta_col_names if key in dictEtiq]
    return plantas,etiquetas

def get_docs_plantas():
    cursor=get_db().cursor()
    cursor.execute('SELECT p.id_planta, p.nombre_ptar, p.doc_diagnostico, '\
                   'pd.pag_indice, pd.pag_informacion, pd.pag_desc, pd.pag_memoria, '\
                   'pd.pag_diag_personal, pd.pag_seguridad, pd.pag_laboratorio, pd.pag_info_hist, pd.pag_trab_campo, '\
                   'pd.pag_desempenio, pd.pag_anexos '\
                   'FROM planta p LEFT JOIN pag_diagnostico pd on pd.planta_id=p.id_planta ')
                   #'WHERE p.doc_diagnostico<>null')
    return cursor.fetchall()

def get_nombres_plantas(filtro=''):
    cursor=get_db().cursor()
    sqlScr='SELECT id_planta, nombre_ptar FROM planta'
    if filtro!='':
        sqlScr+=' where id_planta in ('+filtro+')'
    cursor.execute(sqlScr)
    plantas_personal=cursor.fetchall()    
    return plantas_personal


def get_personal(idPlanta):
    cursor=get_db().cursor()
    cursor.execute('SELECT id_personal, nombre, puesto, tipo, escolaridad, DATE_FORMAT(fecha_ingreso,"%d/%m/%y") as fecha_ingreso, ant_planta, DATE_FORMAT(fecha_puesto,"%d/%m/%y") as  fecha_puesto, ant_puesto '\
                    ' FROM personal where planta_id ='+idPlanta)
    personal=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    #print(personal)
    salida=jsonify(personal)
    print(salida)
    return salida

def get_info_planta(idPlanta):
    cursor=get_db().cursor()
    sqlScr=("SELECT tipo_documento_id FROM info_planta WHERE planta_id="+idPlanta)
    cursor.execute(sqlScr)
    rowsTipoDoc=cursor.fetchall()
    print(rowsTipoDoc)
    if rowsTipoDoc!=[]:
        listaIdsTipoDoc=[str(reg[0]) for reg in rowsTipoDoc]
        strIdsTD=','.join(listaIdsTipoDoc)
        sqlScr="INSERT INTO info_planta(planta_id, tipo_documento_id) (SELECT "+idPlanta+",id_tipo_documento FROM tipo_documento "\
           "WHERE id_tipo_documento not in ("+strIdsTD+"))"
    else:
        sqlScr="INSERT INTO info_planta(planta_id, tipo_documento_id) (SELECT "+idPlanta+",id_tipo_documento FROM tipo_documento )"
    cursor.execute(sqlScr)
    g.db.commit()
    sqlScr='SELECT ip.planta_id, ip.tipo_documento_id, td.tipo_documento as documento,ip.entregado,ip.cant_arch_digitales, '\
           'ip.tam_arch_digitales,ip.tam_fisico, DATE_FORMAT(ip.fecha_recepcion,"%d/%m/%y") as fecha_recepcion, ip.observaciones FROM info_planta ip LEFT JOIN tipo_documento td'\
            ' ON td.id_tipo_documento=tipo_documento_id '\
            ' WHERE planta_id='+idPlanta    
    cursor.execute(sqlScr)
    salida = [dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    salida=jsonify(salida)
    print (salida)
    return salida

def get_resmuestreo_caudales(idPlanta):
    cursor=get_db().cursor()
    cursor.execute('SELECT * '\
                    ' FROM resmuestra_caudal where planta_id ='+idPlanta)
    resmuestras=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    #print(personal)
    salida=jsonify(resmuestras)
    #print(salida)
    return salida

def get_datosgraf_resmuestreo_caudales(idPlanta):
    cursor=get_db().cursor()
    cmdSQL='select a.muestra,a.caudal as caudal_influente,b.caudal as caudal_efluente, '\
                    ' a.ph as ph_influente, b.ph as ph_efluente, '\
                    ' a.temp as temp_influente, b.temp as temp_efluente '\
                    ' from resmuestra_caudal a, resmuestra_caudal b '\
                    ' where b.planta_id=a.planta_id and b.muestra=a.muestra and a.tipo="Influente" and b.tipo="Efluente" and a.muestreo=b.muestreo and a.muestreo=1 '\
                    ' and a.planta_id = '+idPlanta
    cursor.execute(cmdSQL)
    print(cmdSQL)
    resmuestras=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    #print(personal)
    salida=jsonify(resmuestras)
    #print(salida)
    return salida

def get_resmuestreo_compuesta(idPlanta):
    cursor=get_db().cursor()
    cursor.execute('SELECT tipo, solsed, sst, dbo5, nt, pt, hh, dqo, color_a436, color_a525, color_a620, color_alph, arsenico, cadmio, cobre, cromo, mercurio, niquel, plomo, zinc '\
                    ' FROM resmuestra_compuesta where planta_id ='+idPlanta+' and muestreo = 1 ')
    resmuestras=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    #print(personal)
    salida=jsonify(resmuestras)
    print(salida)
    return salida

def get_resmuestreo_tox(idPlanta):
    cursor=get_db().cursor()
    cursor.execute('SELECT tipo, muestra, ce50_5, ce50_15, ce50_30, ut_5, ut_15, ut_30 '\
                    ' FROM resmuestra_tox where planta_id ='+idPlanta+' and muestreo = 1 ')
    resmuestras=[dict((cursor.description[i][0], value) \
               for i, value in enumerate(row)) for row in cursor.fetchall()]
    #print(personal)
    salida=jsonify(resmuestras)
    print(salida)
    return salida

def identifica_usuario(usuario):
    try: 
        cursor=get_db().cursor()
        sql= """SELECT id_usuario,nombre_usuario,clave,rol_id,nombre,apellido_paterno,apellido_materno,
                    telefono_movil,activo FROM usuario WHERE nombre_usuario='{}'  """.format(usuario.nombre_usuario)
        cursor.execute(sql)
        row=cursor.fetchone()
        if (row!=None):
            usuario=Usuario(row[0], row[1], Usuario.verifica_clave(row[2], usuario.clave), row[3],row[4],row[5],row[6],row[7],row[8])
            return usuario
        else:
            return None
    except Exception as ex:
        raise Exception(ex)


def busca_usuario_por_id(id):
    try: 
        cursor=get_db().cursor()
        sql= """SELECT id_usuario,nombre_usuario,rol_id,nombre,apellido_paterno,apellido_materno,
                    telefono_movil,activo FROM usuario WHERE id_usuario={} """.format(id)
        cursor.execute(sql)
        row=cursor.fetchone()
        if (row!=None):
            usuario=Usuario(row[0], row[1], None, row[2],row[3],row[4],row[5],row[6],row[7])
            return usuario
        else:
            return None
    except Exception as ex:
        raise Exception(ex)