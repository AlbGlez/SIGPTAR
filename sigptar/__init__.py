import os
from flask import Flask, render_template, session, request, redirect, url_for, flash
from .db import get_plantas, get_docs_plantas, get_nombres_plantas, get_personal, get_info_planta, \
                get_resmuestreo_caudales, get_datosgraf_resmuestreo_caudales, get_resmuestreo_compuesta, get_resmuestreo_tox
from flask_login import LoginManager,login_user,logout_user, login_required,current_user

from .models.Usuario import Usuario



def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    # manejo de usuarios loggeados
    login_manager_app=LoginManager(app)
    app.config.from_mapping(
        SECRET_KEY='dev'
        #DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
        #print ("SECRET: " + str(app.secret_key))
        #print (app.config['DBCONFIG'])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @login_manager_app.user_loader
    def load_user(id_usuario):
        return db.busca_usuario_por_id(id_usuario)
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('Login'))

    @app.route('/')
    def Raiz():
        if ( current_user.is_active):
            return redirect(url_for('Inicio'))    
        else:
            return redirect(url_for('Login'))
        #return render_template('inicio.html')

    @app.route('/inicio')
    @login_required
    def Inicio():
        return render_template('inicio.html')

    @app.route('/login', methods=['GET','POST'])
    def Login():
        if ((request.method=='POST') and (request.form['formId']!=None)):
            if ('checkAsAnonimo' in request.form):
                frm_usr='anonimo'
                frm_password='anonimo'
            else:
                frm_usr=request.form['usuario']
                frm_password=request.form['password']
            print(frm_usr)
            print(frm_password)
                
            usuario=Usuario(0,frm_usr,frm_password)
            usuario_identificado=db.identifica_usuario(usuario)
                
            if usuario_identificado!=None:
                if (usuario_identificado.clave):
                    login_user(usuario_identificado)
                    return redirect(url_for('Inicio'))
                else:
                    flash("Clave incorrecta")
                    return render_template('identifica.html')
            else:
                flash("Usuario no registrado")
                return render_template('identifica.html')
        else:
            return render_template('identifica.html')

    @app.route('/localizacion', methods=['POST','GET'])
    @login_required
    def Localiza():
        plantas, etiquetas=get_plantas()
        return render_template('localiza.html', lista_plantas=plantas, etiquetas_plantas=etiquetas)

    @app.route('/diagnostico')
    @login_required
    def Diagnostico():
        secc=request.args.get("seccion")
        titulo=request.args.get("titulo_seccion")
        docs_plantas=get_docs_plantas();
        print(secc);
        return render_template('doc_diagnostico.html',lista_plantas=docs_plantas,seccion_ini=secc,titulo_sec=titulo)

    @app.route('/datos_personal')
    @login_required
    def DatosPersonal():
        plantas=get_nombres_plantas('Select distinct planta_id from personal')
        return render_template('datos_personal.html',lista_plantas=plantas)

    @app.route('/consulta_personal')
    @login_required
    def ConsultaPersonal():
        planta=request.args.get("planta")
        if planta is None:
            return  []
        else:
            return  get_personal(planta)

    @app.route('/info_plantas')
    @login_required
    def InfoPlantas():
        plantas=get_nombres_plantas()
        return render_template('info_plantas.html',lista_plantas=plantas)

    @app.route('/consulta_info_planta')
    @login_required
    def consulta_info_planta():
        planta=request.args.get("planta")
        print("Consulta info planta: "+planta)
        if planta != None:
            return  get_info_planta(planta)        
        return []

    @app.route('/resultados_muestreos')
    @login_required
    def ResMuestreos():
        return "<br><b> Pendiente </b>"
    

    @app.route('/resmuestreo_caudales')
    @login_required
    def ResMuestreoCaudales():
        plantas=get_nombres_plantas()
        return render_template('resmuestreo_caudales.html',lista_plantas=plantas)

    @app.route('/consulta_resmuestreo_caudales')
    @login_required
    def consulta_resmuestreo_caudales():
        planta=request.args.get("planta")
        print("Consulta info planta: "+planta)
        if planta != None:
            return  get_resmuestreo_caudales(planta)        
        return []


    @app.route('/consulta_datosgraf_resmuestreo_caudales')
    @login_required
    def consulta_datosgraf_resmuestreo_caudales():
        planta=request.args.get("planta")
        print("Consulta info planta: "+planta)
        if planta != None:
            return  get_datosgraf_resmuestreo_caudales(planta)        
        return []

    @app.route('/resmuestreo_compuesta')
    @login_required
    def ResMuestreoCompuesta():
        plantas=get_nombres_plantas()
        return render_template('resmuestreo_compuesta.html',lista_plantas=plantas)

    @app.route('/consulta_resmuestreo_compuesta')
    @login_required
    def consulta_resmuestreo_compuesta():
        planta=request.args.get("planta")
        print("Consulta info planta rm_compuesta: "+planta)
        if planta != None:
            return  get_resmuestreo_compuesta(planta)        
        return []

    @app.route('/resmuestreo_toxicidad')
    @login_required
    def ResMuestreoTox():
        plantas=get_nombres_plantas()
        return render_template('resmuestreo_tox.html',lista_plantas=plantas)

    @app.route('/consulta_resmuestreo_tox')
    @login_required
    def consulta_resmuestreo_tox():
        planta=request.args.get("planta")
        print("Consulta info planta rm_tox: "+planta)
        if planta != None:
            return  get_resmuestreo_tox(planta)        
        return []
    return app

