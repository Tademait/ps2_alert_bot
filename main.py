import discord, json, math, schedule, time, sys, os
from dotenv import load_dotenv
from datetime import datetime
import urllib.request as urlreq

load_dotenv()

TOKEN = os.getenv('TOKEN')
if (TOKEN == None):
    print("Error: .env file with bot token not found.")
    sys.exit(1)

client = discord.Client()

# TODO get more complex info about the events, distinguish between main alerts and smaller events
# TODO add "!alert info" parameters to let the user choose server and optional details + add argument parser for this
# TODO in addition to parsing more info, edit the embed messages and their looks (possibly use custom emotes and images)
# TODO add timer to periodically check for updates on the main alerts and game news (this will probably also need
# a place to store the users preferred server ID to check on
# TODO clean the code (most importantly imports) and repo, hide internal files, add aditional error handling,
# write down the README and some basic usage and functionality info + screenshots on the repo main page


def getEventInfo():
    try:
        with urlreq.urlopen(
                "https://census.daybreakgames.com/get/ps2:v2/world_event/?type=METAGAME&world_id=13&c:limit=1", timeout=10) as url:
            data = json.loads(url.read().decode())
    except (urlreq.HTTPError, urlreq.URLError) as error:
        print("An error occured while reqtrieving the data from API: {}", error)
        return "N/A"
    except urlreq.timeout:
        print("Request timed out while retrieving the data from API")
        return "N/A"
    for p in data['world_event_list']:
        event_id = int(p['metagame_event_id'])
        timestamp = int(p['timestamp'])
        event_state = p["metagame_event_state_name"]

    with open("metagame_event.json", "r") as f:
        eventy_txt = f.read()
        eventy_json = json.loads(eventy_txt)

    #   getting the time data
    current_time = math.ceil(datetime.now().timestamp())
    running_time = ((current_time - timestamp) / 60)
    running_time = round(running_time, 2)

    if (event_state == "ended"):    # change this back to started, used only for debugging purposes
        print("STARTED")
    # this if statement filters out only the "main" in-game meta alerts (the event IDs may need a revisit due to a  game update):
    #    if ((158 >= event_id) and (event_id >= 123)) or ((193 >= event_id) and (event_id >= 183)):
        for h in eventy_json["metagame_event_list"]:
            if (event_id == int(h["metagame_event_id"])):
                event_info_name = h["name"]["en"]
                event_info_desc = h["description"]["en"]
                return event_info_name, event_info_desc
    print("no event running")
    return "N/A"    # in case function fails to return a tuple with the info


def getTime():
    return datetime.now().strftime("[%H:%M:%S]:")


@client.event
async def on_ready():
    print("{0} Logged in as {1.user}".format(getTime(), client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # maybe define a complete premade embed instead of just color later
    orange = discord.colour.Color.from_rgb(236, 88, 9)
    if message.content == "!hi":
        hello_embed = discord.Embed(title="UwU", description="Hello {}".format(message.author), color=orange)
        hello_embed.set_image(url="https://cdn.betterttv.net/emote/60448132306b602acc598647/3x.gif")
        await message.channel.send(embed=hello_embed)
    if message.content == "!help":
        await message.channel.send(" !alert info [server name] - prints out the current status on given server.\n"
                                   " !hi - show the bot some attention and love.\n")
    if message.content == "!alert info":
        info = getEventInfo()
        if (info == "N/A"):
            await message.channel.send("No info available")
        else:
            await message.channel.send(info[0] + "\n" + info[1])
client.run(TOKEN)
