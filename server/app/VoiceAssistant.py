#!/usr/bin/python3
# -*- coding: utf-8 -*-
# export GOOGLE_APPLICATION_CREDENTIALS="/Users/msaito/Development/matricis/Baquara/TelegramBot/baquara-ada04c105d60.json"
# export GOOGLE_APPLICATION_CREDENTIALS="$BABILONIA_HOME/server/app/baquara-1620594501016-8cbc77ce86ff.json"

import os
import io
from threading import Thread
from difflib import SequenceMatcher
import json
import logging
import logging.config
import time
import datetime as dt
from typing import Dict
from pymediainfo import MediaInfo
from google.cloud import (speech, storage)
from telegram import (  ReplyKeyboardMarkup,
                        ReplyKeyboardRemove,
                        Update,
                        Message,
                        ChatAction,
                        Voice
                     )

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
BUCKET_NAME = 'bazinga'
#WORKFLOW STATE ID
W_OASIS, W_CONFIRMATION, W_BYE = range(3)


class VoiceAssistant(Thread):
    def __init__(self, cfg, oasis_props, voice_words):
        Thread.__init__(self)
        self.speech_client = speech.SpeechClient()
        self.storage_client = storage.Client()
        self.updater = Updater(cfg["TELEGRAM"]["TOKEN"])
        #self.logger = logging.getLogger(__name__)
        self.oasis = self.filter_oasis(oasis_props)
        self.voice_words = voice_words

    def filter_oasis(self, oasis_props):
        result = {}
        for node in oasis_props:
            if node != "oasis-undefined":
                result[oasis_props[node]['name']] = node
        return result

    def download_and_prep(self, file_name: str, message: Message, voice: Voice) -> bool:
        voice.get_file().download(file_name)
        message.reply_chat_action(action=ChatAction.TYPING)
        return voice.duration > 58

    def transcribe(self, file_name: str, to_gs: bool, lang_code: str = 'pt-BR'):
        media_info = MediaInfo.parse(file_name)
        if len(media_info.audio_tracks) != 1 or not hasattr(media_info.audio_tracks[0], 'sampling_rate'):
            os.remove(file_name)
            raise ValueError('Failed to parse sample rate')
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=media_info.audio_tracks[0].sampling_rate,
            enable_automatic_punctuation=False,
            language_code=lang_code)

        try:
            if to_gs:
                bucket = self.storage_client.get_bucket(bucket_or_name=BUCKET_NAME)
                blob = bucket.blob(file_name)
                blob.upload_from_filename(file_name)
                audio = speech.RecognitionAudio(uri='gs://%s/%s' % (BUCKET_NAME, file_name))
                response = self.speech_client.long_running_recognize(config=config, audio=audio).result(timeout=500)
                blob.delete()
            else:
                with io.open(file_name, 'rb') as audio_file:
                    content = audio_file.read()
                audio = speech.RecognitionAudio(content=content)
                response = self.speech_client.recognize(config=config, audio=audio)
        except Exception as e:
            os.remove(file_name)
            raise e

        os.remove(file_name)

        message_text = ''
        for result in response.results:
            message_text += result.alternatives[0].transcript + '\n'

        return message_text

    def voice_to_text(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_message.chat.id
        file_name = '%s_%s%s.ogg' % (chat_id, update.message.from_user.id, update.message.message_id)
        to_gs = self.download_and_prep(file_name, update.effective_message, update.effective_message.voice)

        message_text = self.transcribe(file_name, to_gs)

        if message_text == '':
            update.effective_message.reply_text('Transcription results are empty.')
            return

        update.effective_message.reply_text(self.process(message_text))

        update.effective_message.reply_text(message_text)

    def process(self, message_text):
        print('[MENSAGEM]', message_text)
        words = message_text.split()
        oasis_best_ratio = 0
        command_best_ratio = 0
        oasis = ''
        command = ''
        oasis_listen_name = ''
        command_listen_name = ''
        phrase_len = len(words)
        if phrase_len != 2 :
            return "Comando não reconhecido. Tente <COMAND> <OASIS>"
        listened_cmd = words[0].upper()
        print('[LISTENED CMD]',listened_cmd)
        for meta_data_cmd in self.voice_words['COMMAND']:
            for cmd in self.voice_words['COMMAND'][meta_data_cmd]:
                cmd = cmd.upper()
                ratio =  SequenceMatcher(None, listened_cmd, cmd).ratio()
                if ratio > command_best_ratio:
                    command_best_ratio = ratio
                    command_listen_name = listened_cmd
                    command = meta_data_cmd
        listened_oasis = words[1].upper()
        print('[LISTENED OASIS]',listened_oasis)
        for oasis_name in self.oasis:
            oasis_name = oasis_name.upper()
            ratio =  SequenceMatcher(None, listened_oasis, oasis_name).ratio()
            if ratio > oasis_best_ratio:
                oasis_best_ratio = ratio
                oasis_listen_name = listened_oasis
                oasis = oasis_name
        for all_oasis in self.voice_words['ALL_OASIS']:
            all_oasis = all_oasis.upper()
            ratio =  SequenceMatcher(None, listened_oasis, all_oasis).ratio()
            if ratio > oasis_best_ratio:
                oasis_best_ratio = ratio
                oasis_listen_name = listened_oasis
                oasis = all_oasis
        if oasis_best_ratio > 0 and command_best_ratio >0:
            response = '[OASIS] '+ oasis_listen_name+' '+ oasis+' '+str(oasis_best_ratio) + '\n'
            response = response+'[CMD] '+ command_listen_name+' '+ command+' '+str(command_best_ratio)

            print(response)
            return response

    def begining(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user.first_name

        keyboard = [["Irrigar", "Suspender irrigação"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(
            f'Olá, {user}. Tudo bem? eu sou o assistente da babilônia!\n\n'
            'O que deseja fazer?',
            reply_markup=reply_markup,)
        return W_OASIS

    def action(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user.first_name
        action =  update.message.text
        print(f'User {user} start chat and wants to {action}.')
        user_data = context.user_data
        user_data['action'] = action
        f = lambda A, n=4: [A[i:i+n] for i in range(0, len(A), n)]
        keyboard = f(list(self.oasis.keys()))

        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(
            'Qual Oasis?',
            reply_markup=reply_markup,
        )
        return W_CONFIRMATION

    def confirmation(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user.first_name
        oasis =  update.message.text
        user_data = context.user_data
        user_data['oasis'] = oasis
        action = context.user_data['action']
        print(f'Confirm => User: {user} Action: {action} Oasis: {oasis}.')

        message = f' Deseja {action} a {oasis} agora?'

        keyboard = [["Prosseguir", "Encerrar"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        update.message.reply_text(
            message,
            reply_markup=reply_markup,)

        return W_BYE

    def cancel(self, update: Update, _: CallbackContext) -> int:
        user = update.message.from_user
        print(f'Usuário {user} cancelou a conversa.')
        update.message.reply_text(
            'Tchau! Espero conversar com você em breve', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def working(self, update: Update, context: CallbackContext) -> int:
        user = update.message.from_user
        oasis = context.user_data['oasis']
        action = context.user_data['action']
        print(f'Confirmed => User: {user} Action: {action} Oasis: {oasis}.')
        update.message.reply_text(
            'Ainda não terminamos essa funcionalidade 😞'
        )
        return ConversationHandler.END

    def run(self) -> None:
        # Get the dispatcher to register handlers
        dispatcher = self.updater.dispatcher

        voice_handler = MessageHandler(Filters.voice, self.voice_to_text, run_async=True)
        dispatcher.add_handler(voice_handler)
        dispatcher.add_handler(ConversationHandler(
            entry_points=[  CommandHandler('iniciar', self.begining),
                            MessageHandler(Filters.text, self.begining)
            ],
            states={
                W_OASIS:[
                        MessageHandler(Filters.text, self.action)],
                W_CONFIRMATION:[
                        MessageHandler(Filters.text, self.confirmation)],
                W_BYE:[
                        CommandHandler('Prosseguir', self.working),
                        CommandHandler('Encerrar', self.cancel)],
            },
            fallbacks=[CommandHandler('parar', self.cancel)],
        ))

        # Start the Bot
        self.updater.start_polling()
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        #self.updater.idle()

if __name__ == '__main__':
    print("STARTING TelegramBot")

    with open('config.json', "r") as config_json_file:
        cfg = json.load(config_json_file)

    with open('../../common/oasis_properties.json', "r") as oasis_prop_file:
        oasis_properties = json.load(oasis_prop_file)

    with open('../../common/voice_words.json', "r") as voice_words_file:
        voice_words = json.load(voice_words_file)

    with open('logging.json', "r") as logging_json_file:
        logging_config = json.load(logging_json_file)
        logging.config.dictConfig(logging_config)

    bot = VoiceAssistant(cfg, oasis_properties, voice_words)
    bot.start()
