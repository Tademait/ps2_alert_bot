import discord, json, math, schedule, time, sys, os
from dotenv import load_dotenv
from datetime import datetime
import urllib.request as urlreq
import threading
import asyncio

# TODO get more complex info about the events, distinguish between main alerts and smaller events
# TODO add "!alert info" parameters to let the user choose server and optional details + add argument parser for this
# TODO in addition to parsing more info, edit the embed messages and their looks (possibly use custom emotes and images)
# TODO add timer to periodically check for updates on the main alerts and game news (this will probably also need
# a place to store the users preferred server ID to check on
# TODO clean the code (most importantly imports) and repo, hide internal files, add aditional error handling,
# write down the README and some basic usage and functionality info + screenshots on the repo main page
# add a restart command for reloading the script or modules
# add role checking to enable some of the commands only for specific roles
# register service for API access at the daybreak server
# clean the background threads (especially the old threading one) and check if create_task works properly
# make some epic usable and programmer-friendly API / [whatever it should be called] so that the adding of new functionality
# to the app is as simple as possible (generalised printing through arguements, generalised grabbing of info from api...)

# QoL IDEAS:
#   check if there's map queue in game and if so, for which server
#   check which servers are currently unlocked and locked
#   add time remaining in addition to time elapsed (or just keep remaining time till the end of alert)

checking_enabled = False

def getEventInfo(serverNumber):
    try:
        with urlreq.urlopen(
                f"https://census.daybreakgames.com/get/ps2:v2/world_event/?type=METAGAME&world_id={serverNumber}&c:limit=1", timeout=10) as url:
            data = json.loads(url.read().decode())
    except (urlreq.HTTPError, urlreq.URLError) as error:
        print("An error occured while retrieving the data from API: {error}")
        return "N/A"
    #except urlreq.timeout:
    #   print("Request timed out while retrieving the data from API")
    #    return "N/A"
    try:
        for p in data['world_event_list']:
            event_id = int(p['metagame_event_id'])
            timestamp = int(p['timestamp'])
            event_state = p["metagame_event_state_name"]
            factionPercentage = []
            factionPercentage.append("🟦 NC: " + p["faction_nc"][0:4] + "%")
            factionPercentage.append("🟥 TR: " + p["faction_tr"][0:4] + "%")
            factionPercentage.append("🟪 VS: " + p["faction_vs"][0:4] + "%")
    except KeyError:
        console_print("An error occured while parsing the json file")
        print(data)
        return "N/A"
    try:
        filepath = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(filepath, "metagame_event.json")
        with open(filepath, "r") as f:
            eventy_txt = f.read()
            eventy_json = json.loads(eventy_txt)
    except:
        print("Error reading the file metagame_event.json")
        return "N/A"
    #   getting the time data
    current_time = math.ceil(datetime.now().timestamp())
    running_time = ((current_time - timestamp) / 60)
    running_time = round(running_time, 2)
    running_time = str(running_time)

    if (event_state == "ended"):
        return "ENDED"
    if (event_state == "started"):    # change this back to started, used only for debugging purposes
    # this if statement filters out only the "main" in-game meta alerts (the event IDs may need a revisit due to a game update):
    #    if ((158 >= event_id) and (event_id >= 123)) or ((193 >= event_id) and (event_id >= 183)):
        for entry in eventy_json["metagame_event_list"]:
            if (event_id == int(entry["metagame_event_id"])):
                event_info_name = entry["name"]["en"]
                event_info_desc = entry["description"]["en"]
                return event_info_name, event_info_desc, running_time, factionPercentage
    print("no event running")
    return "N/A"    # in case function fails to return a tuple with the info

async  def sendHelloInfo(message):
    orange = discord.colour.Color.from_rgb(236, 88, 9)
    hello_embed = discord.Embed(title="UwU", description="Hello {}".format(message.author), color=orange)
    hello_embed.set_image(url="https://cdn.betterttv.net/emote/60448132306b602acc598647/3x.gif")
    await message.channel.send(embed=hello_embed)

async def sendAlertInfo(message, server):
    orange = discord.colour.Color.from_rgb(236, 88, 9)
    serverDict = {
        "connery"   : 1,
        "cobalt"    : 13,
        "miller"    : 10,
        "emerald"   : 17,
        "soltech"   : 40,
        "jaeger"    : 19
    }
    try:
        info = getEventInfo(serverDict[server])
    except:
        await message.channel.send("Wrong server name") # More like "something happened in getEventInfo"!!!
        return
    if (info == "N/A"):
        await message.channel.send("No info available")
        return
    if (info == "ENDED"):
        alert_embed = discord.Embed(title=f"Currently running events on {server}:",
                                    description="There is no event running at the moment", color=orange)
        await message.channel.send(embed=alert_embed)
    else:
        alert_embed = discord.Embed(title=f"Currently running events on {server}:", description="\n", color=orange)
        alert_embed.add_field(name=info[0], value=info[1] + "\n" + "Elapsed time: " + info[2] + " minutes", inline=True)
        alert_embed.add_field(name="Current score", value=info[3][0] + " " + info[3][1] + " " + info[3][2], inline=True)
        alert_embed.set_footer(text=message.author,
                               icon_url="https://logo-logos.com/wp-content/uploads/2018/03/discordlogo.png")
        await message.channel.send(embed=alert_embed)


async def sendHelpInfo(message):
    orange = discord.colour.Color.from_rgb(236, 88, 9)
    help_embed = discord.Embed(title="Help", description="Usable bot commands: ", color=orange)
    help_embed.add_field(name="?alert info [server name]", value="prints out the current status on given server.",
                         inline=False)
    help_embed.add_field(name="?hi", value="show the bot some attention and love.", inline=False)
    await message.channel.send(embed=help_embed)


async def sendDevMessages(message, contents):
    print("{0} {1}".format(getTime(), contents))
    await message.channel.send(contents)

def getTime():
    return datetime.now().strftime("[%H:%M:%S]:")

def console_print(contents):
    print("{0} {1}".format(getTime()), contents)

def background_check(message):
    global something_is_up
    while checking_enabled:
        print("standard threading loop is running too")
        time.sleep(5)


async def background_check_asynchronous(message):
    while checking_enabled:
        print("henlo, async loop bezi")
        await asyncio.sleep(120)
        info = getEventInfo(13)
        if info != "N/A" and info != "ENDED":
            print("info contains: " + str(info))
            await sendAlertInfo(message, "cobalt")

def main():
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    if (TOKEN == None):
        print("Error: .env file with bot token not found.")
        sys.exit(1)

    client = discord.Client()
    @client.event
    async def on_ready():
        print("{0} Logged in as {1.user}".format(getTime(), client))

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        # maybe define a complete premade embed instead of just color later
        orange = discord.colour.Color.from_rgb(236, 88, 9)
        if message.content == "?hi":
            await sendHelloInfo(message)

        if message.content == "?help":
            await sendHelpInfo(message)

        if message.content.startswith("?alert info"):
            server = str(message.content).split()[-1].lower()
            if server == "info":
                await sendAlertInfo(message, "cobalt")
            else:
                await sendAlertInfo(message, server)

        bg_thread = threading.Thread(name='background', target=background_check, args=[message])
        if message.content == "?enable notifications" or message.content == "?en":
            global checking_enabled
            checking_enabled = True
            asyncio.create_task(background_check_asynchronous(message)) # edit to make sure the create_task method is not spawning more threads each time the check is activated!!
            if not bg_thread.is_alive():
                bg_thread.start()
            await sendDevMessages(message, "Automatic event check has been enabled")

        if message.content == "?disable notifications" or message.content == "?dn":
            checking_enabled = False
            await sendDevMessages(message, "Automatic event check has been disabled")
    client.run(TOKEN)


if __name__ == "__main__":
    main()


