import time
import socket
import platform
from random import randint
import schedule
from requests import get
from links import Links


def get_info():
    '''gets oauth token from file'''
    with open(info_path) as file:
        return file.readlines()[0].rstrip()

def get_rand_clip():
    '''gets a random line from clips.txt'''
    with open(clips_path, "r") as file:
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
    s.send(bytes("PRIVMSG #" + NICK + " :" + msg + "\r\n", "UTF-8"))

def stats_command(msg):
    user = msg.replace("!stats", "")
    if user.startswith(" ") and len(user) > 4:
        user = user[1:]
        epic_id = get_epic_id(user)
        if epic_id:
            stats = get_fort_stats(epic_id)
            if stats:
                send_message("WINS: " + str(stats[0]) + ", K/D: " + str(stats[1]) + ", WIN %: " + str(stats[2]))
            else:
                send_message("ERROR - user found, but couldn't get stats for some reason ResidentSleeper")
        else:
            send_message("ERROR - cannot find username: '" + user + "'")
    else:
        send_message("ERROR - incorrect format: !stats <epic-username>")

def randclip_command():
    send_message("https://clips.twitch.tv/" + get_rand_clip())

def followage_command(msg, user):
    name = msg.replace("!followage", "")
    if name.startswith(" ") and len(name) > 4:
        name = name[1:]
    else:
        name = user
    followage = get("https://api.crunchprank.net/twitch/followage/RealYungZ/" + name + "?precision=3").text
    send_message(followage)

def retweet_command():
    req = get("https://api.crunchprank.net/twitter/latest/RealYungZ?no_rts&url").text
    send_message(req)

def uptime_command():
    new_time = time.time()
    uptime = time.strftime("%H hours %M minutes", time.gmtime(new_time - start_time))
    send_message("RealYungZ has been live for " + uptime)

def lovemeter_command(msg, name):
    name = msg.replace("!lovemeter", "")
    if name.startswith(" ") and len(name) > 2:
        name = name[1:]
        send_message(name + " is " + str(randint(0, 100)) + "% in love with " + name)
    else:
        send_message("ERROR - incorrect format: !lovemeter <anything>")

def check_mod(name):
    req = get("http://tmi.twitch.tv/group/user/realyungz/chatters").json()
    if name in req['chatters']['moderators']:
        return True
    return False

def handle_viewer_command(name, message):
    if message.startswith("!stats"):
        stats_command(message)
    elif message.startswith("!randclip"):
        randclip_command()
    elif message.startswith("!followage"):
        followage_command(message, name)
    elif message.startswith("!retweet"):
        retweet_command()
    elif message.startswith("!uptime"):
        uptime_command()
    elif message.startswith("!lovemeter"):
        lovemeter_command(message, name)
    elif message.startswith("!sub"):
        send_message(Links.SUB)
    elif message.startswith("!tip"):
        send_message(Links.TIP)
    elif message.startswith("!discord"):
        send_message(Links.DISCORD)
    elif message.startswith("!twitter"):
        send_message(Links.TWITTER)
    elif message.startswith("!youtube"):
        send_message(Links.YOUTUBE)
    elif message.startswith("!keyboard"):
        send_message(Links.KEYBOARD)
    elif message.startswith("!mouse"):
        send_message(Links.MOUSE)
    elif message.startswith("!fortstats"):
        send_message(Links.FORTSTATS)
    elif message.startswith("!pc"):
        send_message(Links.PC)
    elif message.startswith("!res"):
        send_message("1600x1080p")
    elif message.startswith("!hugme"):
        send_message("/me hugs "+ name)
    elif message.startswith("!code"):
        send_message("Code for my twitch bot is here realyuSly " + Links.CODE)

def handle_mod_command(name, message):
    if check_mod(name):
        if message.startswith("&amimod"):
            send_message("you are a mod realyuSwag")
    else:
        send_message("you is not a mod ResidentSleeper")

def youtube_timer():
    send_message("Check out my latest youtube video <3 https://www.youtube.com/watch?v=6LX_D-pDfdI")

def discord_timer():
    send_message("come hang in me discord realyuSwag " + Links.DISCORD)

info_path = ""
clips_path = ""

if platform.system() is "Windows":
    info_path = "C:\\Users\\Angie\\Desktop\\info.txt"
    clips_path = "C:\\Users\\Angie\\Dev\\twitchb0t\\clips.txt"
else:
    info_path = "/mnt/c/Users/Angie/Desktop/info.txt"
    clips_path = "/mnt/c/Users/Angie/Dev/twitchb0t/clips.txt"

HOST = "irc.twitch.tv"
PORT = 6667
NICK = "realyungz"
PASS = get_info()
start_time = time.time()

schedule.every(8).to(12).minutes.do(youtube_timer)
schedule.every(8).to(12).minutes.do(discord_timer)

s = socket.socket()
s.connect((HOST, PORT))
s.send(bytes("PASS " + PASS + "\r\n", "UTF-8"))
s.send(bytes("NICK " + NICK + "\r\n", "UTF-8"))
s.send(bytes("JOIN #" + NICK + "\r\n", "UTF-8"))


while True:
    LINE = str(s.recv(1024))
    if "End of /NAMES list" in LINE:
        print("authenticated")
        break

while True:
    for line in str(s.recv(1024)).split('\\r\\n'):
        schedule.run_pending()
        parts = line.split(':')
        if len(parts) < 3:
            continue

        if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
            message = parts[2][:len(parts[2])]
        else:
            continue

        if message.startswith("!"):
            username = parts[1].split("!")[0]
            handle_viewer_command(username, message)
        elif message.startswith("&"):
            username = parts[1].split("!")[0]
            handle_mod_command(username, message)
