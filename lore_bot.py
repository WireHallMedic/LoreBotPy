import discord
import json
import re
import random
import time
from mock import mockify, addMock, rmMock

notYetImplementedStr = ":warning: This feature is not yet implemented :warning:"
profanityChirp = []
mockList = []
lastSwear = 0
chirpForSwearing = False
swearingCooldown = 0
mapFileName = 'world_map.jpg';

# let's load some things from files
token = open("token.txt", "r").read()
msgDict = json.loads(open("messages.json","r").read())
deityDict = json.loads(open("deities.json","r").read())
geoDict = json.loads(open("geography.json","r").read())
hakimDict = json.loads(open("hakim.json","r").read())
historyDict = json.loads(open("history.json","r").read())
standardsDict = json.loads(open("standards.json","r").read())
timeDict = json.loads(open("time.json","r").read())
langDict = json.loads(open("languages.json","r").read())
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
   outFile = None
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
         outStr = updateProfanityCount(authorName, key == "fuck", len(re.findall(key, cmd)))
         if outStr == None and chirpForSwearing:
            outStr = getProfanityResponse()
   
   if re.search("^shut it.*lorebot", cmd) != None or re.search("^shut up.*lorebot", cmd) != None:
      if authorName == "wire_hall_medic":
         outStr = "Yessir."
      else:
         outStr = "No thank you, " + authorName
   
   # ignore messages that don't start with a bang, unless mocking
   if outStr == None and message.content[0] != "!" and authorName.lower() not in mockList:
      return
   
   # bot info and ToC
   if cmd == "lorebot":
      outStr = msgDict["botInfo"]
      for key in msgDict["recognizedCommands"]:
         outStr += "\n  " + key + " " + msgDict["recognizedCommands"][key]
   elif cmd == "status":
      outStr = msgDict["goodStatus"]
   
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
   elif cmd == "languages":
      outStr = getLangStr()
   elif cmd == "map":
      outFile = getImageFromFile(mapFileName)
   elif re.search("lunar", cmd) != None:
      outStr = parseLunar(cmd)
   
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
      if re.search("^!mock", message.content) != None:
         if authorName == "wire_hall_medic" or authorName == "SJ":
            outStr = addMock(message.content, mockList)
         else:
            outStr = "Nah."
   
   if outStr == None:
      if re.search("^!unmock", message.content) != None:
         outStr = rmMock(message.content, mockList)
   
   if outStr == None:
      for key in deityDict:
         if key == cmd or key == cmdNoThe:
            outStr = "**{}**\nPortfolio: {}\nAlignment: {}\nCaste: {}\nSymbol: {}\nDescription: {}".format( \
               deityDict[key]["name"], deityDict[key]["portfolio"], deityDict[key]["alignment"], deityDict[key]["caste"], \
               deityDict[key]["symbol"], deityDict[key]["description"])
   
   # post image
   # this is a lazy implementation. It should read ./images, check if there's a matching file, and then post it 
   # if there is one
   if outStr == None:
      imageFile = ""
      if cmd == "dick pic" or cmd == "dickpic":
         imageFile = "dick_pic.png" # this is a picture of Dick Van Dyke. Have some class.
      if cmd == "get off my lawn" or cmd == "getoffmylawn":
         imageFile = "get_off_my_lawn.png"
      if cmd == "gift":
         imageFile = "gift.png"
      if imageFile != "":
         with open(imageFile, 'rb') as f:
            picture = discord.File(f)
            await channel.send(file=picture)
            return
   
   if outStr != None:
      outStr = outStr.replace("[CUR_YEAR_NUM]", str(stateDict["current year number"]))
      outStr = outStr.replace("[CUR_YEAR_WORDS]", stateDict["current year words"])
      outStr = outStr.replace("[CUR_AGE_NUM]", str(stateDict["current age number"]))
      outStr = outStr.replace("[CUR_AGE_WORDS]", stateDict["current age words"])
      outStr = outStr.replace("[NAME]", authorName)
      outStr = outStr.replace("[BAD_ODDS]", str(roll(50) + 50))
   
   # mock, if applicapable
   if authorName.lower() in mockList:
      if outStr == None:
         outStr = message.content
      outStr = mockify(outStr)
   
   # print results
   if outFile != None:
      await message.channel.send(file=outFile)
   if outStr != None:
      await message.channel.send(outStr)

#strip message for processing
def cleanMessage(str):
   newStr = str
   if newStr[0] == "!":
      newStr = newStr[1:]
   newStr = newStr.lower()
   newStr = newStr.strip()
   return newStr

# RNGesus
def roll(val):
   return random.randint(1, val)

# list languages
def getLangStr():
   length = 0
   str = ""
   for key in langDict:
      length = max(length, len(langDict[key]["name"]) + 3)
   for key in langDict:
      str += getLangLine(key, length)
   return "```" + str + "```"

# get language line
def getLangLine(key, desiredLen):
   str = langDict[key]["name"]
   for i in range(len(langDict[key]["name"]), desiredLen):
      str += " "
   str += langDict[key]["spoken_by"]
   if langDict[key]["notes"] != "":
      str += " (" + langDict[key]["notes"] + ")"
   str += "\n"
   return str

# only gives a chirp back every 30 seconds
def getProfanityResponse():
   global lastSwear
   curTime = time.time()
   if curTime <= lastSwear + swearingCooldown:
      return None
   lastSwear = curTime
   return random.choice(profanityChirp)

# update profanity count
def updateProfanityCount(author, isFuck, swearcount):
   authorTotalStr = "{}_t".format(author)
   authorFBombStr = "{}_f".format(author)
   outStr = None
   for i in range(swearcount):
      if authorTotalStr in swearCountDict:
         swearCountDict[authorTotalStr] = swearCountDict[authorTotalStr] + 1
      else:
         swearCountDict[authorTotalStr] = 1
      if authorFBombStr not in swearCountDict:
         swearCountDict[authorFBombStr] = 0
      if isFuck:
         swearCountDict[authorFBombStr] = swearCountDict[authorFBombStr] + 1
      if swearCountDict[authorTotalStr] == 10:
         outStr = ":trophy:Achievement Unlocked: Potty Mouth!\n[NAME] has sworn 10 times!\nEnter command '!swear count' to see your stats!"
      if swearCountDict[authorTotalStr] == 100:
         outStr = ":trophy:Achievement Unlocked: Advanced Potty Mouth!\n[NAME] has sworn 100 times!\nEnter command '!swear count' to see your stats!"
      if swearCountDict[authorTotalStr] == 1000:
         outStr = ":trophy:Achievement Unlocked: Master Potty Mouth!\n[NAME] has sworn 1000 times!\nEnter command '!swear count' to see your stats!"
   # save current state
   with open('swearcount.json', 'w') as json_file:
      json.dump(swearCountDict, json_file)
   return outStr
   
def getSwearCount(author):
   authorTotalStr = "{}_t".format(author)
   authorFBombStr = "{}_f".format(author)
   if authorTotalStr in swearCountDict:
      return "Since I began counting, user [NAME] has sworn {} times, of which {} were f-bombs.".format( \
         swearCountDict[authorTotalStr], swearCountDict[authorFBombStr])
   return "I have no swearing on record for user [NAME]."

def getPercentStr(cyclePos):
   cyclePercent = int((cyclePos * 100) + .5)
   if cyclePercent > 50:
      cyclePercent = 50 - (cyclePercent - 50)
   cyclePercent *= 2
   return "{:d}%".format(cyclePercent)

def getPhaseStr(dayNum, cycleLen):
   cyclePos = (dayNum % cycleLen) / cycleLen
   waxWane = "Waning"
   if cyclePos < .5:
      waxWane = "Waxing"
   return "{} ({})".format(getPercentStr(cyclePos), waxWane)

def calcLunar(day, year):
   day += (year * 360)
   return "Elmore: {}\nKaja: {}".format(getPhaseStr(day, 39), getPhaseStr(day, 27))

def parseLunar(inStr):
   strArr = inStr.split()
   # we should have four: 'lunar', season, day, year
   try:
      day = int(strArr[2])
      if re.search("^sp", strArr[1]):
         day += 0
      elif re.search("^su", strArr[1]):
         day += 90
      elif re.search("^au", strArr[1]):
         day += 180
      elif re.search("^fa", strArr[1]):
         day += 180
      elif re.search("^wi", strArr[1]):
         day += 270
      return calcLunar(day, int(strArr[3]))
   except:
      return msgDict["lunarParsingFailure"].format(inStr)

def getImageFromFile(fileName):
   with open(fileName, 'rb') as f:
      return discord.File(f)

# fire this bad boy up
client.run(token)