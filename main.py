import json
import logging
import os

import firebase_admin
from discord.ext import commands
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

from FiexmoCog import FiexmoCog
from Settings import FiexmoSettingStore

# setup some logging stuff
discord_logger = logging.getLogger('discord')
discord_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
discord_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
discord_logger.addHandler(discord_handler)

app_logger = logging.getLogger('fiexmo')
app_handler = logging.FileHandler(filename='fiexmo.log', encoding='utf-8', mode='w')
app_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
app_logger.addHandler(app_handler)

logging.basicConfig(level=logging.INFO)

# load envs
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
FIREBASE_CRED = os.getenv('FIREBASE_ADMIN')

cred = credentials.Certificate(json.loads(FIREBASE_CRED))
firebase_admin.initialize_app(cred)


# mime types we're approving to be posted
# TODO: make configurable
APPROVED_MIMES = ["video", "image", "audio", "text"]

# setup setting storage
db = firestore.client()  # this connects to our Firestore database
fiexmo_store = FiexmoSettingStore(db)

# setup bot and cog
bot = commands.Bot(command_prefix='%')
bot.add_cog(FiexmoCog(bot, fiexmo_store, app_logger, APPROVED_MIMES))
bot.run(TOKEN)
