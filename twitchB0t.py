import socket
import schedule
import time
from requests import get
from random import randint
from links import Links
import platform


def get_info():
    with open(info_path) as f:
        return f.readlines()[0].rstrip()

def get_rand_clip():
    with open(clips_path, "r") as f:
        lines = f.readlines()
        return lines[randint(0, len(lines) - 1)]

def request(url):
    r = get(url).json()
    return r

def get_epic_id(username):
    r = request("https://fortnite-public-api.theapinetwork.com/prod09/users/id?username=" + username)
    if 'uid' in r:
        return r['uid']
    else:
        return None

def get_fort_stats(id):
    r = request("https://fortnite-public-api.theapinetwork.com/prod09/users/public/br_stats_v2?user_id=" + id)
    print(r)
    if 'overallData' not in r:
        return None
    if 'defaultModes' in r['overallData']:
        stats   = r['overallData']['defaultModes']
        if type(stats) is list:
            return None
        items = {'kills':0, 'placetop1':0, 'matchesplayed':0}
        for item in items:
            if item in stats:
                items[item] = stats[item]
        kd = round(float(items['kills']) / float(items['matchesplayed'] - items['placetop1']), 2)
        win_ratio = round(float(items['placetop1'] / items['matchesplayed']) * 100, 2)
        return [items['placetop1'], kd, win_ratio]
    else:
        return None

def send_message(message):
    s.send(bytes("PRIVMSG #" + NICK + " :" + message + "\r\n", "UTF-8"))

def stats_command(message):
    username = message.replace("!stats", "")
    if username.startswith(" ") and len(username) > 4:
        username = username[1:]
        id = get_epic_id(username)
        if id:
            stats = get_fort_stats(id)
            if stats:
                send_message("WINS: " + str(stats[0]) + ", K/D: " + str(stats[1]) + ", WIN %: " + str(stats[2]))
            else:
                send_message("ERROR - user found, but couldn't get stats for some reason ResidentSleeper")
        else:
            send_message("ERROR - cannot find username: '" + username + "'")
    else:
        send_message("ERROR - incorrect format: !stats <epic-username>")

def randclip_command():
    send_message("https://clips.twitch.tv/" + get_rand_clip())

def followage_command(message, username):
    name = message.replace("!followage", "")
    if name.startswith(" ") and len(name) > 4:
        name = name[1:]
    else:
        name = username
    followage = get("https://api.crunchprank.net/twitch/followage/RealYungZ/" + name + "?precision=3").text
    send_message(followage)

def retweet_command():
    rt = get("https://api.crunchprank.net/twitter/latest/RealYungZ?no_rts&url").text
    send_message(rt)

def uptime_command():
    new_time = time.time()
    uptime = time.strftime("%H hours %M minutes", time.gmtime(new_time - start_time))
    send_message("RealYungZ has been live for " + uptime)

def lovemeter_command(message, username):
    name = message.replace("!lovemeter", "")
    if name.startswith(" ") and len(name) > 2:
        name = name[1:]
        send_message(username + " is " + str(randint(0,100)) + "% in love with " + name)
    else:
        send_message("ERROR - incorrect format: !lovemeter <anything>")

def check_mod(username):
    r = get("http://tmi.twitch.tv/group/user/realyungz/chatters").json()
    if username in r['chatters']['moderators']:
        return True
    return False

def handle_viewer_command(username, message):
    if message.startswith("!stats"):
        stats_command(message)
    elif message.startswith("!randclip"):
        randclip_command()
    elif message.startswith("!followage"):
        followage_command(message, username)
    elif message.startswith("!retweet"):
        retweet_command()
    elif message.startswith("!uptime"):
        uptime_command()
    elif message.startswith("!lovemeter"):
        lovemeter_command(message, username)
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
        send_message("/me hugs "+ username)

def handle_mod_command(username, message):
    if check_mod(username):
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

if platform is "Windows":
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
    line = str(s.recv(1024))
    if "End of /NAMES list" in line:
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
