import telebot
from telebot import types
import mysql.connector
import re
import time

bot = telebot.TeleBot("6749423598:AAGfnilTkPriB9g9XutRL9u7XsmaeLixPGY")
# @bot.message_handler(commands=["help", "start"])


@bot.message_handler(func=lambda message: True)
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton('Ya atendi ticket', callback_data="ticket")
    item2 = types.InlineKeyboardButton('Estoy atendiendo tema urgente', callback_data="TemaUrgente")
    markup.add(item1, item2)
    user_id = message.chat.id
    bot.send_message(message.chat.id, "ID: " + str(user_id))
    bot.send_message(user_id, text='Es tu turno de atender ticket, puedes responder aqui mismo cuando confirmes que ya fue tu turno', reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def answer(callback):
    if callback.message:
        if callback.data == 'ticket':
            mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
            host = "localhost",
            user = "root",
            password = "S3d1t3c!",
            database = 'turnos'
            )
            mycursor = mydb.cursor()
            mycursor.execute("SELECT * from personas;")
            data = mycursor.fetchall()
            if (int(data[0][1]) == callback.message.chat.id):
                mycursor.execute("DELETE FROM personas where numero = '"+data[0][1]+"';")
                mycursor.execute("INSERT into personas VALUES ('"+ data[0][0] +"', '"+data[0][1]+"');")
                notificacion = int(data[0][1])
                notificacionNombre = data[0][0]
                notificacionproximo = int(data[1][1])
                bot.send_message(notificacion, "Ticket tomado!")
                time.sleep(5)
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Ya atendi ticket', callback_data="ticket")
                item2 = types.InlineKeyboardButton('Estoy atendiendo tema urgente', callback_data="TemaUrgente")
                markup.add(item1, item2)
                bot.send_message(notificacionproximo, "Es tu turno de atender ticket, puedes responder aqui mismo cuando confirmes que ya fue tu turno", reply_markup=markup)
                mycursor.execute("INSERT INTO logs VALUES (now(), 'El usuario "+ notificacionNombre +" tomo su turno');")
                mydb.commit()
                mydb.close()
            else:
                bot.send_message(callback.message.chat.id, "No es tu turno")
                mycursor.execute("INSERT INTO logs VALUES (now(), 'El usuario "+ str(callback.message.chat.id) +" intento tomar un turno ageno');")
                mydb.commit()
                mydb.close()
                #bot.send_message(callback.message.chat.id, "Ticket tomado!")
        if callback.data == 'TemaUrgente':
            mydb = mysql.connector.connect(             #Credenciales de conexion para la base de datos local
            host = "localhost",
            user = "root",
            password = "S3d1t3c!",
            database = 'turnos'
            )

            mycursor = mydb.cursor()
            mycursor.execute("SELECT * from personas;")
            data = mycursor.fetchall()
            if (int(data[0][1]) == callback.message.chat.id):
                mycursor.execute("DELETE FROM personas where numero = '"+data[0][1]+"';")
                mycursor.execute("INSERT into personas VALUES ('"+ data[0][0] +"', '"+data[0][1]+"');")
                notificacionNombre = data[0][0]
                notificacion = int(data[0][1])
                notificacionSarahi = 6988786753 #Escribir numero de Sarahi
                notificacionproximo = int(data[1][1])
                bot.send_message(notificacion, "Ticket saltado, se notificara al administrador!")
                time.sleep(5)
                markup = types.InlineKeyboardMarkup(row_width=1)
                item1 = types.InlineKeyboardButton('Ya atendi ticket', callback_data="ticket")
                item2 = types.InlineKeyboardButton('Estoy atendiendo tema urgente', callback_data="TemaUrgente")
                markup.add(item1, item2)
                bot.send_message(notificacionproximo, "Es tu turno de atender ticket, puedes responder aqui mismo cuando confirmes que ya fue tu turno", reply_markup=markup)
                bot.send_message(notificacionSarahi, "El ingeniero " + notificacionNombre + " salto su turno debido a que esta atendiendo tema urgente")
                mycursor.execute("INSERT INTO logs VALUES (now(), 'El usuario "+ notificacionNombre +" omitio su turno');")
                mydb.commit()
                mydb.close()
            else:
                bot.send_message(callback.message.chat.id, "No es tu turno")
                mycursor.execute("INSERT INTO logs VALUES (now(), 'El usuario "+ str(callback.message.chat.id) +" intento tomar un turno ageno');")
                mydb.commit()
                mydb.close()

if __name__ == '__main__':
    bot.polling(none_stop=True)