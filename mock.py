# for mocking users

def mockify(sourceStr):
   outStr = ""
   toggle = False
   for i in range(len(sourceStr)):
      if toggle:
         outStr += sourceStr[i].upper()
      else:
         outStr += sourceStr[i].lower()
      toggle = not toggle
   return outStr

def addMock(cmd, mockList):
   target = cmd.replace("!mock", "")
   targetLower = target.strip().lower()
   mockList.append(targetLower)
   return "Now mocking user {}.".format(target)

def rmMock(cmd, mockList):
   target = cmd.replace("!unmock", "")
   targetLower = target.strip().lower()
   if targetLower in mockList:
      mockList.remove(targetLower)
      return "Ceasing mocking of user {}.".format(target)
   else:
      return "User {} not in list of users currently being mocked.".format(target)

if __name__ == "__main__":
   str = "The wizard quickly jinxed the gnomes before they vaporized."
   print(mockify(str))