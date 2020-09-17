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

if __name__ == "__main__":
   str = "The wizard quickly jinxed the gnomes before they vaporized."
   print(mockify(str))