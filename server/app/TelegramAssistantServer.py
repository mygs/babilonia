#!/usr/bin/python3
# -*- coding: utf-8 -*-
# export GOOGLE_APPLICATION_CREDENTIALS="$BABILONIA_HOME/server/app/baquara-1620594501016-8cbc77ce86ff.json"

import os
import io
from difflib import SequenceMatcher
import json
import pandas
import logging
import logging.config
import requests

from Models import DB, TelegramSession
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker

from flask import Flask, request
from telegram import (  ReplyKeyboardMarkup,
                        ReplyKeyboardRemove,
                        Update,
                        Message,
                        ChatAction,
                        Voice,
                        ParseMode
                     )

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

ACTION_START = "Irrigar"
ACTION_STOP = "Suspender irrigação"
GO = "Prosseguir"
NOGO = "Encerrar"
#WORKFLOW STATE ID
W_OASIS, W_DURATION, W_CONFIRMATION, W_BYE = range(4)


SERVER_HOME = os.path.dirname(os.path.abspath(__file__))
COMMON_DIR=os.path.join(SERVER_HOME, '../../common')
os.chdir(SERVER_HOME) #change directory because of log files
with open(os.path.join(SERVER_HOME, 'config.json'), "r") as config_json_file:
    cfg = json.load(config_json_file)

with open(os.path.join(COMMON_DIR, 'oasis_properties.json'), "r") as oasis_prop_file:
    oasis_props = json.load(oasis_prop_file)

with open(os.path.join(SERVER_HOME, 'logging.json'), "r") as logging_json_file:
    logging.config.dictConfig(json.load(logging_json_file))
    logger = logging.getLogger(__name__)

with open( os.path.join(COMMON_DIR, 'voice_words.json'), "r") as voice_words_file:
    voice_words = json.load(voice_words_file)

class TelegramAssistantServer():
    app = None
    def __init__(self):
        self.app = Flask(self.__class__.__name__)
        self.logger = logger
        self.cfg = cfg
        self.updater = Updater(cfg["TELEGRAM"]["TOKEN"])
        self.SQLALCHEMY_DATABASE_URI =  cfg["SQLALCHEMY_DATABASE_URI"]
        self.oasis = self.filter_oasis(oasis_props)
        self.user_data_cache = {}
        self.logger.info("[TelegramAssistantServer] instantiated")


    def filter_oasis(self, oasis_props):
        result = {}
        for node in oasis_props:
            if node != "oasis-undefined":
                result[oasis_props[node]['name']] = node
        return result

    def save_chat_id(self, user_name, chat_id):

        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        session = sessionmaker(bind=engine)()
        data = TelegramSession( BOT=self.cfg["TELEGRAM"]["BOT"],
                                USER_NAME=user_name,
                                CHAT_ID= chat_id
                             )
        session.merge(data)
        session.commit()

    def begining(self, update: Update, context: CallbackContext) -> int:
        first_name = update.message.chat.first_name
        chat_id = update.message.chat_id
        self.save_chat_id(first_name, chat_id)
        self.user_data_cache[chat_id] = {}

        keyboard = [[ACTION_START, ACTION_STOP]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(
            f'Olá, {first_name}. Tudo bem? eu sou o assistente da babilônia!\n\n'
            'O que deseja fazer?',
            reply_markup=reply_markup,)
        return W_OASIS

    def action(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user.first_name
        action =  update.message.text
        self.logger.info('[TelegramAssistantServer] User %s start chat and wants to %s.', user, action)
        user_data = context.user_data
        user_data['action'] = action
        f = lambda A, n=4: [A[i:i+n] for i in range(0, len(A), n)]
        keyboard = f(list(self.oasis.keys()))

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(
            'Qual Oasis?',
            reply_markup=reply_markup,
        )
        if user_data['action'] != ACTION_START:
            return W_CONFIRMATION
        else:
            return W_DURATION

    def duration(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user.first_name
        oasis =  update.message.text
        user_data = context.user_data
        user_data['oasis'] = oasis

        keyboard = [["10","30", "60", "120", "180"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(
            f'Irrigar por quantos segundos?',
            reply_markup=reply_markup,)
        return W_CONFIRMATION

    def confirmation(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user.first_name
        user_data = context.user_data
        action = user_data['action']

        if user_data['action'] == ACTION_START:
            duration =  update.message.text
            user_data['duration'] = duration
            oasis = user_data['oasis']
            self.logger.info('[TelegramAssistantServer] TBC: User: %s / Action %s / Oasis: %s / Duration: %s', user, action, oasis, duration)
            message = f'Deseja {action} a {oasis} por {duration} segundos?'
        else:
            oasis =  update.message.text
            user_data['oasis'] = oasis
            self.logger.info('[TelegramAssistantServer] TBC: User: %s / Action %s / Oasis: %s', user, action, oasis)

            message = f'Deseja {action} a {oasis}?'

        keyboard = [[GO, NOGO]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(
            message,
            reply_markup=reply_markup,)

        return W_BYE

    def cancel(self, update: Update, _: CallbackContext) -> int:
        user = update.message.from_user
        self.logger.info('[TelegramAssistantServer] User %s cancelled chat', user)

        update.message.reply_text(
            'Tchau! Espero conversar com você em breve', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END


    def send_requests(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user.first_name
        oasis = context.user_data['oasis']
        action = context.user_data['action']
        self.logger.info('[TelegramAssistantServer] Confirmed: User: %s / Action %s / Oasis: %s', user, action, oasis)

        value = False
        message = '🚫 Irrigação suspensa na <b>'+oasis+'</b>'
        if action == ACTION_START:
            value = True
            message = '💦 Irrigação iniciada na <b>'+oasis+'</b>'
            self.user_data_cache[update.message.chat_id] = context.user_data
            self.set_timer(update, context)

        self.command_water_tank(value)
        self.command_oasis(oasis, value)

        update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    def remove_job_if_exists(self, name: str, context: CallbackContext) -> bool:
        """Remove job with given name. Returns whether job was removed."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True

    def set_timer(self, update: Update, context: CallbackContext) -> None:
        """Add a job to the queue."""
        chat_id = update.message.chat_id
        try:
            due = int(context.user_data['duration'])
            if due < 0:
                return

            job_removed = self.remove_job_if_exists(str(chat_id), context)
            context.job_queue.run_once(self.command_stop_irrigation, due, context=chat_id, name=str(chat_id))

        except (IndexError, ValueError):
            update.message.reply_text('Erro ao agendar o desligamento da irrigação 😞')

    def command_water_tank(self, value) -> int:
        headers = {'Content-type': 'application/json'}
        url = 'http://%s/water-tank'%(self.cfg["WATER_TANK"]["SERVER"])
        json_msg = json.dumps({'DIRECTION':'OUT', 'ACTION':value })
        response = requests.post(url, data=json_msg, headers=headers)
        self.logger.info("[TelegramAssistantServer] /water-tank service response: %s", response)
        if response.status_code != 200:
            self.logger.info("[TelegramAssistantServer] water-tank service connection http status code: %s!!!", str(response.status_code))

    def command_oasis(self, oasis, value) -> int:
        headers = {'Content-type': 'application/json'}
        url = 'http://%s/command'%(self.cfg["TELEGRAM"]["BACKEND_SERVER"])
        json_msg = json.dumps({'NODE_ID': self.oasis[oasis], 'MESSAGE_ID': 'telegram', 'COMMAND':{'WATER':value}})
        response = requests.post(url, data=json_msg, headers=headers)
        self.logger.info("[TelegramAssistantServer] /command service response: %s", response)
        if response.status_code != 200:
            self.logger.info("[TelegramAssistantServer] /command service connection http status code: %s!!!", str(response.status_code))

    def command_stop_irrigation(self, context):
        job = context.job
        chat_id = job.context
        oasis = self.user_data_cache[chat_id]['oasis']
        message = '🚫 Irrigação suspensa na <b>'+oasis+'</b>'
        context.bot.send_message(job.context, text=message, parse_mode=ParseMode.HTML)
        self.command_oasis(oasis, False)
        self.command_water_tank(False)
        self.user_data_cache[chat_id] = {}


    def run(self) -> None:
        # Get the dispatcher to register handlers
        dispatcher = self.updater.dispatcher

        dispatcher.add_handler(ConversationHandler(
            entry_points=[  CommandHandler('iniciar', self.begining),
                            MessageHandler(Filters.text, self.begining)
            ],
            states={
                W_OASIS:[
                        MessageHandler(Filters.text, self.action)],
                W_DURATION:[
                        MessageHandler(Filters.text, self.duration)],
                W_CONFIRMATION:[
                        MessageHandler(Filters.text, self.confirmation)],
                W_BYE:[
                        MessageHandler(Filters.regex("^"+GO+"$"), self.send_requests),
                        MessageHandler(Filters.regex("^"+NOGO+"$"), self.cancel)],
            },
            fallbacks=[CommandHandler('parar', self.cancel)],
        ))

        # Start the Bot
        self.updater.start_polling()
        # Start Flask server
        self.app.add_url_rule('/monitor', methods=['POST'], view_func=self.monitor)
        self.app.run(host='0.0.0.0', port=7171)


    #curl -i -H "Content-Type: application/json" -X POST -d '{"SOURCE":"CURL","MESSAGE":"MESSAGE CONTENT"}' http://localhost:7171/monitor
    def monitor(self):
        message = request.get_json()
        engine = create_engine(self.SQLALCHEMY_DATABASE_URI)
        results = pandas.read_sql_query(
            """
            SELECT CHAT_ID FROM TELEGRAM_SESSION WHERE BOT = '{}'
            """.format(self.cfg["TELEGRAM"]["BOT"]),
            engine)
        for index,result in results.iterrows():
            chat_id = result['CHAT_ID']
            self.logger.info("[monitor] chat_id=%s, source=%s, message=%s", chat_id, message["SOURCE"], message["MESSAGE"])
            self.updater.bot.sendMessage(   chat_id=int(chat_id),
                                            text=message["MESSAGE"],
                                            parse_mode=ParseMode.HTML)
                                            #https://core.telegram.org/bots/api#html-style
        return json.dumps({'status':'Success!'})

    @staticmethod
    def send_monitor_message(message):
        monitor_url = cfg["TELEGRAM"]["MONITOR_URL"]
        headers = {'Content-type': 'application/json'}
        response = requests.post(monitor_url,data=json.dumps(message), headers=headers)
        logger.info("[TelegramAssistantServer] send_message response: %s", response)

        if response.status_code != 200:
            logger.info("[TelegramAssistantServer] send_message http status code: %s!!!", str(response.status_code))

if __name__ == '__main__':
    #print("STARTING TelegramAssistantServer")
    #TelegramAssistantServer.send_monitor_message('{"SOURCE":"CURL","MESSAGE":"MESSAGE CONTENT"}')
    bot = TelegramAssistantServer()
    bot.run()
