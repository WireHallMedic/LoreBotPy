# LoreBotPy

LoreBot is an encyclopedia, intended to supplement role-playing games played over Discord.

LoreBot is not accessable from the chat in a Discord meeting room; this is due to the Discord API. The intended use for bots is to call '!<function name> <arguments>'. However, LoreBot instead reads user chat and responds to '!<topic name>', where topic names are keys in JSON files. Hard-coding topics would dramatically reduce the modularity of LoreBot. Adding a specific wrapper function to call from text chat in a meeting is a possible solution, though would likely be confusing for users.
