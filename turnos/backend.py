from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
import hashlib
import pandas as pd
import re
import json
from flask_session import Session
import requests
from datetime import datetime
import teleflask
from heyoo import WhatsApp
from twilio.rest import Client
import time
import telebot

sid="AC06c0af6be19241cdeba5269c959cd143"
authToken="e0d12ac5402e9747dd2299ca438bdc60"
client=Client(sid,authToken)

app = Flask(__name__, template_folder='./Views')
if __name__ == '__main__':
    app.run(port=5000, debug=True)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = 'b221d9dbb083a7f33428d7c2a3c3198ae925614d70210e28716ccaa7cd4ddb79'

headings = ("Nombre", "Numero")

#Funcion principal que enruta desde la direccion Raiz a cualquier direccionamiento.
@app.route("/", methods= ['GET', 'POST'])
def main():
    if not session['user']:
        return redirect("./login.html")
    else:
        return redirect("index.html")

#Funcion para acciones del Login
@app.route("/login.html", methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
        host = "localhost",
        user = "root",
        password = "S3d1t3c!",
        database = 'turnos'
        )

        mycursor = mydb.cursor()
        user = request.form.get('user')
        password = request.form.get('password')
        password = hashlib.sha256(password.encode()).hexdigest()
        mycursor.execute("SELECT COUNT(user) FROM usuarios where user='" + user + "' and pass='" + password + "';")
        myresults = mycursor.fetchall()
        if myresults[0][0] == 1:
            mycursor.execute("SELECT permiso from usuarios where user='" + user + "' and pass='" + password + "';")
            myresultspermiso = mycursor.fetchall()
            if myresultspermiso[0][0] == 3:
                session['user'] = user
                session['permiso'] = myresultspermiso[0][0]
                mydb.close()
                return redirect("/index.html")
            if myresultspermiso[0][0] == 1:
                session['user'] = user
                session['permiso'] = myresultspermiso[0][0]
                mydb.close()
                return redirect("/usuario.html")
        flash("Credenciales incorrectas", 'warning')
    return render_template("/login.html")

#Funcion para acciones del Registro de 
@app.route("/registro.html", methods= ['GET', 'POST'])
def registro():
    if request.method == 'POST':
        mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
        host = "localhost",
        user = "root",
        password = "S3d1t3c!",
        database = 'turnos'
        )
        mycursor = mydb.cursor()
        user = request.form.get('user')
        password = request.form.get('password')
        passwordconf = request.form.get('passwordconfirm')
        if password == passwordconf:
            password = hashlib.sha256(password.encode()).hexdigest()
            mycursor.execute("SELECT COUNT(user) FROM usuarios where user='"+user+"';")
            myresults = mycursor.fetchall()
            if myresults[0][0] == 0:
                mycursor.execute("INSERT INTO usuarios(user, pass, permiso) VALUES ('"+ user + "', '"+ password + "', 1);")
                mydb.commit()
                mydb.close()
                flash("Registro exitoso", "message")
                return redirect("/login.html")
            else:
                mydb.close()
                flash("Usuario existente", 'warning')
                return redirect("/login.html")
        else:
            mydb.close()
            flash("Registro erroneo", "warning")
            return redirect("/login.html")
    return render_template("/registro.html")

@app.route("/home.html", methods=['GET', 'POST'])
def index():
    if not session['user']:
        return redirect("./login.html")
    if session['permiso'] == 3:
        return redirect("./index.html")
    return redirect("/usuario.html")

@app.route("/enviar.html", methods=['GET', 'POST'])
def enviar():
    if not session['user']:
        return redirect("./login.html")
    if request.method == 'POST':
        mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
        host = "localhost",
        user = "root",
        password = "S3d1t3c!",
        database = 'turnos'
        )
        mycursor = mydb.cursor()
        data = request.form
        dataactivo = data.get('activo')
        dataactivo = dataactivo.replace("\t", "")
        dataactivo = dataactivo.replace("\n", "")
        dataactivo = dataactivo.replace("\r", "")
        dataactivo = re.sub(' +', ' ', dataactivo)
        dataactivo = dataactivo.split()
        if session['user'] == dataactivo[0]:
            dataactivo = dataactivo[1:] + [dataactivo[0]]
            mensaje="Es tu turno de atender ticket"
            
            mycursor.execute("truncate table temppersonas;")
            mycursor.execute("truncate table tempapoyo;")

            i = len(dataactivo)
            x=0
            y=1
            while (x <= i):
                try:
                    mycursor.execute("INSERT INTO temppersonas VALUES ('"+dataactivo[x]+ "', '"+dataactivo[y]+ "');")
                    x= x+2
                    y= x+1
                    mydb.commit()
                except:
                    x= x+1
            
            mycursor.execute("truncate table personas;")
            mycursor.execute("insert into personas select * from temppersonas;")
            mydb.close()
            flash("Turno tomado con exito", 'success')
            print("Turno tomado")
            return redirect("./usuario.html")
        mydb.close()
        flash("No es tu turno", 'warning')
        print("No es tu turno")
    return redirect("./usuario.html")

@app.route("/confirmacion.html", methods=['GET', 'POST'])
def confirmacion():
    if not session['user']:
        return redirect("./login.html")
    if request.method == 'POST':
        mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
        host = "localhost",
        user = "root",
        password = "S3d1t3c!",
        database = 'turnos'
        )
        mycursor = mydb.cursor()
        data = request.form
        dataactivo = data.get('activo')
        datainactivo = data.get('inactivo')
        dataactivo = dataactivo.replace("\t", "")
        dataactivo = dataactivo.replace("\n", "")
        dataactivo = dataactivo.replace("\r", "")
        dataactivo = re.sub(' +', ' ', dataactivo)
        dataactivo = dataactivo.split()
        datainactivo = datainactivo.replace("\t", "")
        datainactivo = datainactivo.replace("\n", "")
        datainactivo = datainactivo.replace("\r", "")
        datainactivo = re.sub(' +', ' ', datainactivo)
        datainactivo = datainactivo.split()

        mycursor.execute("truncate table temppersonas;")

        mycursor.execute("truncate table tempapoyo;")
        i = len(dataactivo)
        x=0
        y=1
        while (x <= i):
            try:
                mycursor.execute("INSERT INTO temppersonas VALUES ('"+dataactivo[x]+ "', '"+dataactivo[y]+ "');")
                x= x+2
                y= x+1

                mydb.commit()
            except:
                x= x+1

        mycursor.execute("truncate table personas;")
        mycursor.execute("insert into personas select * from temppersonas;")
        
        i = len(datainactivo)
        x=0
        y=1
        while (x <= i):
            try:
                mycursor.execute("INSERT INTO tempapoyo VALUES ('"+datainactivo[x]+ "', '"+datainactivo[y]+ "');")
                x= x+2
                y= x+1
                mydb.commit()
            except:
                x= x+1
        mycursor.execute("truncate table apoyo;")
        print("estoy borrando y agregando")
        mycursor.execute("insert into apoyo select * from tempapoyo;")
        print("Termine")
        mydb.commit()
        mydb.close()
        return redirect("./index.html")
    return redirect("./index.html")

@app.route("/index.html", methods=['GET', 'POST'])
def home():
    if not session['user']:
        return redirect("./login.html")
    if request.method == 'POST':
        return redirect("./confirmacion.html")
    mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
    host = "localhost",
    user = "root",
    password = "S3d1t3c!",
    database = 'turnos'
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * from personas;")
    data = mycursor.fetchall()
    mycursor.execute("SELECT * from apoyo;")
    result = mycursor.fetchall()
    mydb.close()
    return render_template("./index.html", headings=headings, data=data, result=result)

@app.route("/usuario.html", methods=['GET', 'POST'])  #FUNCION QUE GENERA LA INTERFAZ DE LOS
def usuario():
    if not session['user']:
        return redirect("./login.html")
    if request.method == 'POST':
        return redirect("/enviar.html")
    mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
    host = "localhost",
    user = "root",
    password = "S3d1t3c!",
    database = 'turnos'
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * from personas;")
    data = mycursor.fetchall()
    mycursor.execute("SELECT * from apoyo;")
    result = mycursor.fetchall()
    mydb.close()
    return render_template("./usuario.html", headings=headings, data=data, result=result)


#Funcion de Logout, sin bugs.
@app.route("/logout.html", methods=['GET', 'POST'])
def logout():
    if session['user']:
        session.pop('user', None)
        session.pop('permiso', None)
        mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
        host = "localhost",
        user = "root",
        password = "S3d1t3c!",
        database = 'turnos'
        )
        mydb.close()
        return redirect("./login.html")