from wxpy import *
bot=Bot()
myfriend=bot.friends().search('王磊',sex=FEMALE)[0]
myfriend.send('test')