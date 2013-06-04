import botcore,socket


#  User Structures:
#     nick, password (md5), email, [valid masks], wins, losses, , admin
#

#server = "bots.esper.net"
server = "irc.jayisgames.com"
port   = 6667

#server = "127.0.0.1"

cry = botcore.CryWolf( server, port, "cry_wolf", "cry[%s]", "#cry_wolf" )

cry.run()
        
