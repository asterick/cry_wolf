#
#  IRC Helper class
#
#  This class handles an IRC stream, and processes the messages
#  to their respective handlers. It is intended to be extended,
#  but you can manually insert functions into it before Run() is called
#

import socket, time

class ChanHandler:
    def Notice( self, target, message ):
        message = message.replace("\r","").split("\n")

        for line in message:
            self.host.cmd( "NOTICE %s :%s" % (target, line) )
        
    def Message( self, target, message ):
        message = message.replace("\r","").split("\n")

        for line in message:
            self.host.cmd( "PRIVMSG %s :%s" % (target, line) )
        
    def Mode( self, args ):
        message = "MODE %s" % (self.channel)

        for arg in args:
            message += " %s" % (arg)

        self.host.cmd( message )

    def Topic( self, topic ):
        self.host.cmd( 'TOPIC %s :%s' % (self.channel, topic) )

    def Part( self ):
        self.host.cmd( "PART %s" % (self.channel) )

    def Kick( self, nick, reason ):
        self.host.cmd( "KICK %s %s :%s" % (self.channel, nick, reason) )

    def Invite( self, nick ):
        self.host.cmd( "INVITE %s %s" % (nick, self.channel) )
        

class IRC:
    def __init__( self, server, port ):
        self.s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

        self.server = server
        self.port = port
        self.queue = []
        self.data = ""

        self.handlers = {
                "001":      self.handlePrinter,
                "002":      self.handlePrinter,
                "003":      self.handlePrinter,
                "004":      self.handleIgnore,  
                "005":      self.handleIgnore,
                "251":      self.handlePrinter,
                "252":      self.handlePrinter,
                "254":      self.handlePrinter,
                "255":      self.handlePrinter,
                "265":      self.handlePrinter,
                "266":      self.handlePrinter,
                "250":      self.handlePrinter,
                "375":      self.handlePrinter,
                "372":      self.handlePrinter,
                "376":      self.handleLoggedIn,
                "422":      self.handleLoggedIn,
                
                "332":      self.handleTopic,
                "302":      self.handleUserHost,
                "433":      self.handleNickCollision,
                "353":      self.handleNames,
                "366":      self.handleIgnore,

                "ping":     self.handlePing,
                
                "error":    self.handleError,
                "privmsg":  self.handleMessage,
                "notice":   self.handleNotice,

                "quit":     self.handleQuit,
                "kick":     self.handleKick,
                "topic":    self.handleTopic,
                "mode":     self.handleMode,
                "join":     self.handleJoined,
                "part":     self.handlePart,
                "nick":     self.handleNewNick,
            }

    def cmd( self, command ):
        self.queue.append( command )
            
    def handleMessage( self, src, args, packet ):        
        self.Message( src, args[0], args[1] )        

    def handleNewNick( self, src, args, packet ):
        self.NickChange( src, args[0] )

    def handleError( self, src, args, packet ):
        self.Error( args[0] )

    def handleNotice( self, src, args, packet ):
        self.Notice(  src, args[0], args[1] )

    def handleNickCollision( self, src, args, packet ):
        self.NickTaken(args[1])

    def handlePrinter( self, src, args, packet ):
        self.ServerMessage( args[1] )

    def handleLoggedIn( self, src, args, packet ):
        self.ServerMessage( args[1] )
        self.Connected()

    def handleQuit( self, src, args, packet ):
        self.Quit( src, args[0] )

    def handleUserHost( self, src, args, packet ):
        self.UserHost( args[0], args[1] )

    def handleNames( self, src, args, packet ):
        self.Names( args[-2], args[-1].split(" ") )

    def handleJoined( self, src, args, packet ):
        self.Joined( args[0], src )

    def handleMode( self, src, args, packet ):
        for i in range(1,len(args)):
            args[i] = args[i]
        
        self.Mode( src, args[0], args[1:] )
                
    def handleKick( self, src, args, packet ):
        self.Kicked( src, args[1], args[0], args[2] )
            
    def handlePart( self, src, args, packet ):        
        self.Parted( args[0], src[:src.find("!")] )

    def handleTopic( self, src, args, packet ):
        self.Topic( src, args[0], args[1] )
        
    def handleIgnore( self, src, args, packet ):
        pass

    def handlePing( self, src, args, packet ):
        print "--- Ping?  Pong!"
        self.cmd( "PONG :%s" % (args[0]) )

    def run( self ):
        self.s.connect( ( self.server, self.port ) )
        self.s.settimeout( 0.25 )
        
        self.Login()

        # --- Setup base time ---
        self.clock = time.time()

        while self.s:
            try:
                recv = self.s.recv(4096).lower()
                if not recv:
                    print "--- Connection Closed"
                    self.s.close()
                    self.s = None
                    return
                data = (self.data+recv).replace("\r","").split("\n")
            except socket.timeout:
                data = []
            except socket.error, msg:
                self.s.close()
                self.s = None
                return
            
            for packet in self.queue:
                self.s.send( packet + '\n' )

            self.queue = []

            # --- Tick time ---
            clock = time.time()
            self.Tick( clock - self.clock )
            self.clock = clock

            if len( data ) < 1:
                continue

#            print self.data, data
            self.data = data[-1]

            for packet in data[:-1]:
                while packet[-1] == " ":
                    packet = packet[:-1]
                
                sourced = packet[0] == ":"
                
                if sourced:
                    packet = packet[1:]
                    
                
                args = []
            
                spl1 = 0

                while True:
                    spl2 = packet.find(" ",spl1)

                    if packet[spl1] == ":":
                        args.append(packet[spl1+1:])
                        break
                    elif spl2 < 0:
                        args.append(packet[spl1:])
                        break
                    else:
                        args.append(packet[spl1:spl2])
                        spl1 = spl2+1

                cmd = args.pop(0)
                if sourced:
                    src = cmd
                    cmd = args.pop(0)
                else:
                    src = self.server

                if cmd in self.handlers:
                    self.handlers[cmd]( src, args, packet )
                else:
                    print "Unhandled responce:", packet 
