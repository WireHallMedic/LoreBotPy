import discord
import json
import re
import random
import time

notYetImplementedStr = ":warning: This feature is not yet implemented :warning:"
profanityChirp = []
lastSwear = 0

# let's load some things from files
token = open("token.txt", "r").read()
msgDict = json.loads(open("messages.json","r").read())
deityDict = json.loads(open("deities.json","r").read())
geoDict = json.loads(open("geography.json","r").read())
hakimDict = json.loads(open("hakim.json","r").read())
historyDict = json.loads(open("history.json","r").read())
standardsDict = json.loads(open("standards.json","r").read())
timeDict = json.loads(open("time.json","r").read())
profanityDict = json.loads(open("profanity.json","r").read())
stateDict = json.loads(open("worldstate.json","r").read())
swearCountDict = json.loads(open("swearcount.json","r").read())

def initBot():
   for key in profanityDict["responses"]:
      profanityChirp.append(profanityDict["responses"][key])

initBot()

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
   for key in profanityDict["naughty words"]:
      if re.search(key, cmd) != None:
         outStr = updateProfanityCount(authorName, re.search("fuck", cmd) != None)
         if outStr == None:
            outStr = getProfanityResponse()
   
   if re.search("^shut it.*lorebot", cmd) != None or re.search("^shut up.*lorebot", cmd) != None:
      if authorName == "wire_hall_medic":
         outStr = "Yessir."
      else:
         outStr = "No thank you, " + authorName
   
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
   
   if re.search("swear count", cmd) != None:
      outStr = getSwearCount(authorName)
      
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
   
   if outStr != None:
      outStr = outStr.replace("[CUR_YEAR_NUM]", str(stateDict["current year number"]))
      outStr = outStr.replace("[CUR_YEAR_WORDS]", stateDict["current year words"])
      outStr = outStr.replace("[CUR_AGE_NUM]", str(stateDict["current age number"]))
      outStr = outStr.replace("[CUR_AGE_WORDS]", stateDict["current age words"])
   
   if outStr is not None:
      outStr = outStr.replace("[NAME]", authorName)
      outStr = outStr.replace("[BAD_ODDS]", str(roll(50) + 50))
   
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

# only gives a chirp back every 10 seconds
def getProfanityResponse():
   global lastSwear
   curTime = time.time()
   if curTime <= lastSwear + 10:
      return None
   lastSwear = curTime
   return random.choice(profanityChirp)

# update profanity count
def updateProfanityCount(author, isFuck):
   authorTotalStr = "{}_t".format(author)
   authorFBombStr = "{}_f".format(author)
   if authorTotalStr in swearCountDict:
      swearCountDict[authorTotalStr] = swearCountDict[authorTotalStr] + 1
   else:
      swearCountDict[authorTotalStr] = 1
   if authorFBombStr not in swearCountDict:
      swearCountDict[authorFBombStr] = 0
   if isFuck:
      swearCountDict[authorFBombStr] = swearCountDict[authorFBombStr] + 1
   # save current state
   with open('swearcount.json', 'w') as json_file:
      json.dump(swearCountDict, json_file)
   if swearCountDict[authorTotalStr] == 10:
      return ":trophy:Achievement Unlocked: Potty Mouth!\n[NAME] has sworn 10 times!\nEnter command '!swear count' to see your stats!"
   if swearCountDict[authorTotalStr] == 100:
      return ":trophy:Achievement Unlocked: Advanced Potty Mouth!\n[NAME] has sworn 100 times!\nEnter command '!swear count' to see your stats!"
   if swearCountDict[authorTotalStr] == 1000:
      return ":trophy:Achievement Unlocked: Master Potty Mouth!\n[NAME] has sworn 1000 times!\nEnter command '!swear count' to see your stats!"
   return None
   
def getSwearCount(author):
   authorTotalStr = "{}_t".format(author)
   authorFBombStr = "{}_f".format(author)
   if authorTotalStr in swearCountDict:
      return "Since I began counting, user [NAME] has sworn {} times, of which {} were f-bombs.".format( \
         swearCountDict[authorTotalStr], swearCountDict[authorFBombStr])
   return "I have no swearing on record for user [NAME]."

# fire this bad boy up
client.run(token)