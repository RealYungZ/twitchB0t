'''to make pylint happy again'''
import time
import socket
import platform
from random import randint
import re
import dataclasses as dc
import typing
import schedule
from requests import get
from links import Links


@dc.dataclass(frozen=True)
class Command:
    '''command class'''
    name: str
    expr: str
    doc: str
    callback: typing.Callable


@dc.dataclass(frozen=True)
class Bot:
    name: str
    commands: dict = dc.field(default_factory=dict)

    def on(self, expr, name=None, doc=None):
        def decorator(fn):
            nonlocal name
            nonlocal doc
            if name is None:
                name = expr
            if doc is None:
                doc = fn.__doc__ or expr
            cmd = Command(name, expr, doc, fn)
            self.commands[name] = cmd
            return fn
        return decorator

    def dispatch_message(self, msg, auth):
        '''checks if a message is indeed a command'''
        for cmd in self.commands.values():
            match = re.match(cmd.expr, msg, re.I)
            if match:
                cmd.callback(self, match, auth)
                return True
        return False

def get_info():
    '''gets oauth token from file'''
    with open(INFO_PATH) as file:
        return file.readlines()[0].rstrip()

def get_rand_clip():
    '''gets a random line from clips.txt'''
    with open(CLIPS_PATH, "r") as file:
        lines = file.readlines()
        return lines[randint(0, len(lines) - 1)]

def request(url):
    '''helper function for get request, returns json'''
    req = get(url).json()
    return req

def get_epic_id(user):
    '''function takes an epic username, the accounts user id is returned'''
    req = request("https://fortnite-public-api.theapinetwork.com/prod09/users/id?username=" + user)
    if 'uid' in req:
        return req['uid']
    return None

def get_fort_stats(epic_id):
    '''get fortnite stats based on an epic id'''
    req = request("https://fortnite-public-api.theapinetwork.com/prod09/users/public/br_stats_v2?user_id=" + epic_id)
    print(req)
    if 'overallData' not in req:
        return None
    if 'defaultModes' in req['overallData']:
        stats = req['overallData']['defaultModes']
        if isinstance(stats, list):
            return None
        items = {'kills':0, 'placetop1':0, 'matchesplayed':0}
        for item in items:
            if item in stats:
                items[item] = stats[item]
        kdr = round(float(items['kills']) / float(items['matchesplayed'] - items['placetop1']), 2)
        win_ratio = round(float(items['placetop1'] / items['matchesplayed']) * 100, 2)
        return [items['placetop1'], kdr, win_ratio]
    return None

def send_message(msg):
    '''sends a message to twitch chat'''
    sock.send(bytes("PRIVMSG #" + NICK + " :" + msg + "\r\n", "UTF-8"))

def check_mod(name):
    '''checks for mod on a given twitch username'''
    req = get("http://tmi.twitch.tv/group/user/realyungz/chatters").json()
    if name in req['chatters']['moderators']:
        return True
    return False

def youtube_timer():
    '''youtube timer for schedule'''
    send_message("Check out my latest youtube video <3 https://www.youtube.com/watch?v=6LX_D-pDfdI")

def discord_timer():
    '''discord timer for schedule'''
    send_message("come hang in me discord realyuSwag " + Links.DISCORD)

def handle_viewer_command(msg):
    '''handle the easy commands'''
    if msg.startswith("!sub"):
        send_message(Links.SUB)
    elif msg.startswith("!tip"):
        send_message(Links.TIP)
    elif msg.startswith("!discord"):
        send_message(Links.DISCORD)
    elif msg.startswith("!twitter"):
        send_message(Links.TWITTER)
    elif msg.startswith("!youtube"):
        send_message(Links.YOUTUBE)
    elif msg.startswith("!keyboard"):
        send_message(Links.KEYBOARD)
    elif msg.startswith("!mouse"):
        send_message(Links.MOUSE)
    elif msg.startswith("!fortstats"):
        send_message(Links.FORTSTATS)
    elif msg.startswith("!pc"):
        send_message(Links.PC)
    elif msg.startswith("!res"):
        send_message("1600x1080p")
    elif msg.startswith("!code"):
        send_message("Code for my twitch bot is here realyuSly " + Links.CODE)

def handle_mod_command(name, msg):
    '''checks if user is mod, determines command used then runs the neccessary funtion'''
    if check_mod(name):
        if msg.startswith("&amimod"):
            send_message("you are a mod realyuSwag")
    else:
        send_message("you is not a mod ResidentSleeper")


bot = Bot("simplebot")

@bot.on("!hugme")
def handle_hugme(bot, match, auth):
    '''handle hugme command'''
    send_message(f"/me hugs {auth}")

@bot.on("!uptime")
def handle_uptime(bot, match, auth):
    '''handles returning the uptime'''
    new_time = time.time()
    uptime = time.strftime("%H hours %M minutes", time.gmtime(new_time - START_TIME))
    send_message("RealYungZ has been live for " + uptime)

@bot.on("!retweet")
def handle_retweet(bot, match, auth):
    '''gets latest tweet'''
    req = get("https://api.crunchprank.net/twitter/latest/RealYungZ?no_rts&url").text
    send_message(req)

@bot.on("!randclip")
def handle_randclip(bot, match, auth):
    '''sends a random clip'''
    send_message("https://clips.twitch.tv/" + get_rand_clip())

@bot.on("!lovemeter\s*(.+)?", name="!lovemeter [anything]")
def handle_lovemeter(bot, match, auth):
    '''handles lovemeter command'''
    name = match.group(1)
    if name:
        send_message(auth + " is " + str(randint(0, 100)) + "% in love with " + name)
    else:
        send_message("ERROR - incorrect format: !lovemeter <anything>")

@bot.on("!followage\s*(.+)?", name="!followage [user]")
def handle_followage(bot, match, auth):
    """get followage time for a twitch user"""

    user = match.group(1)
    if user:
        followage = get("https://api.crunchprank.net/twitch/followage/RealYungZ/" + user + "?precision=3").text
        send_message(followage)
    else:
        send_message("ERROR - incorrect format: !followage <username>")

@bot.on("!stats\s*(.+)?", name="!stats [user]")
def handle_stats(bot, match, auth):
    """Get the stats for a user"""

    user = match.group(1)
    if user:
        epic_id = get_epic_id(user)
        if epic_id:
            stats = get_fort_stats(epic_id)
            if stats:
                send_message(f"Stats for {user} are: WINS: {str(stats[0])}, K/D: {str(stats[1])}, WIN %: {str(stats[2])}")
            else:
                send_message("ERROR - user found, but couldn't get stats for some reason ResidentSleeper")
        else:
            send_message(f"ERROR - cannot find username: '{user}'")
    else:
        send_message("ERROR - incorrect format: !stats <epic-username>")

@bot.on("^!help$", name="!help")
def handle_help(bot, match, auth):
    """Print out the help text for all bot commands"""

    send_message(", ".join(bot.commands))


INFO_PATH = ""
CLIPS_PATH = ""

if platform.system() == "Windows":
    INFO_PATH = "C:\\Users\\Angie\\Desktop\\info.txt"
    CLIPS_PATH = "C:\\Users\\Angie\\Dev\\twitchb0t\\clips.txt"
else:
    INFO_PATH = "/mnt/c/Users/Angie/Desktop/info.txt"
    CLIPS_PATH = "/mnt/c/Users/Angie/Dev/twitchb0t/clips.txt"

HOST = "irc.twitch.tv"
PORT = 6667
NICK = "realyungz"
PASS = get_info()
START_TIME = time.time()

schedule.every(8).to(12).minutes.do(youtube_timer)
schedule.every(8).to(12).minutes.do(discord_timer)

sock = socket.socket()
sock.connect((HOST, PORT))
sock.send(bytes("PASS " + PASS + "\r\n", "UTF-8"))
sock.send(bytes("NICK " + NICK + "\r\n", "UTF-8"))
sock.send(bytes("JOIN #" + NICK + "\r\n", "UTF-8"))


while True:
    LINE = str(sock.recv(1024))
    if "End of /NAMES list" in LINE:
        print("authenticated")
        break

while True:
    for line in str(sock.recv(1024)).split('\\r\\n'):
        schedule.run_pending()
        parts = line.split(':')
        if len(parts) < 3:
            continue

        if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
            message = parts[2][:len(parts[2])]
        else:
            continue

        if message.startswith("!"):
            author = parts[1].split("!")[0]
            if not bot.dispatch_message(message, author):
                handle_viewer_command(message)
        elif message.startswith("&"):
            author = parts[1].split("!")[0]
            handle_mod_command(author, message)
