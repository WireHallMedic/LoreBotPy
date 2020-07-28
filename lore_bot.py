import discord
import json
import re
import random


# let's load some things from files
token = open("token.txt", "r").read()
msgDict = json.loads(open("messages.json","r").read())
deityDict = json.loads(open("deities.json","r").read())
geoDict = json.loads(open("geography.json","r").read())
hakimDict = json.loads(open("hakim.json","r").read())
historyDict = json.loads(open("history.json","r").read())
standardsDict = json.loads(open("standards.json","r").read())
timeDict = json.loads(open("time.json","r").read())

notYetImplementedStr = ":warning: This feature is not yet implemented :warning:"

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord')
    
@client.event
async def on_message(message):
   # don't respond to self or empty messages
   if message.author == client.user or \
      len(message.content) == 0:
      return
   
   # format input
   cmd = cleanMessage(message.content)
   cmdNoThe = cmd.replace("the ", "")
   outStr = None
   authorName = re.sub("#.*", "", str(message.author))
   
   # chirps
   for key in msgDict["chirp"]:
      if re.search(key, cmd) != None:
         outStr = msgDict["chirp"][key]
         break
   if re.search("what does lorebot think", cmd) != None:
      if authorName == "wire_hall_medic":
         outStr = msgDict["chirp"]["_lorebot_thinks_m"]
      else:
         outStr = msgDict["chirp"]["_lorebot_thinks_not_m"]
   if outStr is not None:
      outStr = outStr.replace("[NAME]", authorName)
      outStr = outStr.replace("[BAD_ODDS]", str(roll(50) + 50))
   
   # ignore messages that don't start with a bang
   if outStr == None and message.content[0] != "!":
      return
   
   # bot info and ToC
   if cmd == "lorebot":
      outStr = msgDict["botInfo"]
      for key in msgDict["recognizedCommands"]:
         outStr += "\n  " + key + " " + msgDict["recognizedCommands"][key]
   
   # major topics
   if cmd == "deities":
      outStr = deityDict["deities"]
   elif cmd == "geography":
      outStr = geoDict["geography"]
   elif cmd == "history":
      outStr = historyDict["history"]
   elif cmd == "hakim":
      outStr = hakimDict["hakim"]
   elif cmd == "hakim prices":
      outStr = hakimDict["prices"]
   elif cmd == "time":
      outStr = timeDict["time"]
   elif cmd == "standards":
      outStr = standardsDict["standards"]
   elif re.search("lunar", cmd) != None:
      outStr = notYetImplementedStr
   
   
   #specific topics
   if outStr == None:
      for key in geoDict:
         if key == cmd or key == cmdNoThe:
            outStr = "**{}**\nLanguage: {}\n{}".format(geoDict[key]["name"], geoDict[key]["language"], geoDict[key]["description"])
   
   if outStr == None:
      for key in historyDict:
         if key == cmd or key == cmdNoThe:
            outStr = historyDict[key]
            
   if outStr == None:
      for key in deityDict:
         if key == cmd or key == cmdNoThe:
            outStr = "**{}**\nPortfolio: {}\nAlignment: {}\nCaste: {}\nSymbol: {}\nDescription: {}".format( \
               deityDict[key]["name"], deityDict[key]["portfolio"], deityDict[key]["alignment"], deityDict[key]["caste"], \
               deityDict[key]["symbol"], deityDict[key]["description"]) 
   
   # print results
   if outStr != None:
      await message.channel.send(outStr)

def cleanMessage(str):
   newStr = str
   if newStr[0] == "!":
      newStr = newStr[1:]
   newStr = newStr.lower()
   newStr = newStr.strip()
   return newStr

def roll(val):
   return random.randint(1, val)

# fire this bad boy up
client.run(token)