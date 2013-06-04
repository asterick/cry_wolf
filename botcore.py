import irc, socket, players, types, helpsys

from maskhelp import *
from random import *

msgWelcome = "Welcome, %s, to CRY_WOLF: The Game.  This is a blaitant rip off of the flash game available at: http://www.crywolfgame.com . For more information, message me #HELP.  Oh, the game is buggy."
msgReturn  = "Welcome back %s!  Feel free to join any of the game available to you.  Remember, the game is still being debugged"
wolfMsg    = "You are a wolf!  Help protect your fellow wolves, and remember, don't get caught! (Wolves: %s)"
sheepMsg   = "You are a sheep!  You better hurry up and figure out who is after you, your life depends on it! There are %i wolves on the prowl."
huntMsg    = "The sheep sleep soundly, it is time for you to choose your victim!"
sleepMsg   = "Rest well, but don't sleep soundly!  The wolves are on the prowl"

believeState = [ "%s and yourself were out drinking late together.",
                 "You were watching television with %s all evening.",
                 "%s and yourself have a very lengthy conversation for the entire night" ]
noTrustState = [ "You saw %s leaving the dormatories suspiciously late...",
                 "%s hung up on you, stating they were 'busy'",
                 "%s has been avoiding you for the entire evening" ]
gameStartMsg = "A local towns person was murdered today... and someone in this room did it."

#
#  TODO Listing:
#  Add a "Someone is quiet" notice
#

class Lobby(irc.ChanHandler):
    def __init__( self, host, channel, botnick, players ):
        self.players = players
        self.botnick = botnick
        self.host    = host
        self.channel = channel

        self.Topic( 'CRY_WOLF: The IRC Game (Lobby)' )
        self.Mode( ['+ntl 100'] )
        self.nicks = []

    def close( self ):
        self.players.write()

    def mode( self, args ):
        pass
    
    def names( self, nicks ):
        for player in self.nicks:
            self.players.dereference( nick )

        self.nicks = []
        
        for nick in nicks:
            if nick[0] == "+" or nick[0] == "@":
                nick = nick[1:]                

            self.nicks.append( nick )
            self.players.reference( nick )

    def join( self, nick ):
        shortName = nick[:nick.find("!")]
        self.nicks.append( nick )
        self.players.reference( shortName )
        login = self.players.login( nick )  # Passive login

        if login and not self.players.loggedIn( shortName ):
            self.Notice( shortName, msgWelcome % (shortName) )
        else:
            self.Notice( shortName, msgReturn % (shortName) )
        
    def part( self, nick ):
        if nick in self.nicks:
            del self.nicks[ self.nicks.index( nick ) ]
            self.players.dereference( nick )

        if nick == self.botnick:
            self.host.cmd( "QUIT :Lost access to the lobby" )

    def Tick( self, ticks ):
        pass

    def nick( self, old, new ):
        if new in self.nicks:
            del self.nicks[ self.nicks.index( new ) ]
            self.players.dereference( new )
        self.nicks.append( new )
        self.players.reference( new )

    def message( self, source, message ):
        # --- Need to keep track of flooding here ---        
        pass

class GameControl(irc.ChanHandler):
    def __init__( self, host, channel, botnick, players ):
        self.players = players
        self.botnick = botnick
        self.channel = channel
        self.host    = host

        self.people  = []

        self.gameStarted = False
        self.gameOver    = False

        self.minPlayers  = 7
        self.maxPlayers  = 15
        self.delibTime   = 3*60
        self.voteTime    = 1*60
        self.killTime    = 2*60

        self.sheep       = []
        self.wolves      = []
        self.eliminated  = []
        self.oustedSheep = {}

        self.votes       = {}
        self.options     = []

        self.Timer       = self.DieOnEmpty
        self.Overflow    = 60

        self.TopicTemp   = "CRY_WOLF: Waiting..."
        self.TopicCount  = -1

    def close( self ):
        for player in self.people:
            player = player
            self.players.dereference( player )
            self.host.leaveGame( player, self )

        self.people = []        
        self.host.DeactiveGame( self.channel )
        self.players.write()

    def SetTopic( self, topic ):
        self.TopicTemp = topic
        self.TopicCount = -1

    def join( self, nick ):
        nick = nick
        shortName = nick[:nick.find("!")]

        if self.gameStarted:
            self.Kick( shortName, 'Sorry, this game has already started' )
            return
        elif self.host.inGame( shortName ):
            self.Kick( shortName, 'You are already participating in a game' )

        self.Mode( ['+v', shortName] )
        self.players.reference( shortName )

        self.people.append( shortName )

        self.host.UpdateGame(self.channel,len(self.people))  

        waitingOn = self.minPlayers - len(self.people)

        if waitingOn > 0:
            self.Topic( 'CRY_WOLF: Waiting for %i players' % (waitingOn) )
            self.Timer = None
        else:
            self.SetTopic( 'CRY_WOLF: Game starting...' )

            if self.Timer != self.StartGame:
                self.Timer = self.StartGame
                self.Overflow = 30

        self.host.enterGame( shortName, self )

    def nick( self, old, new ):
        self.Kick( new, 'Mid-game nick changes forbidden, enjoy abandon.' )
        self.part( old )
        
    def part( self, nick ):
        nick = nick
        if nick == self.botnick or nick not in self.people:
            return
        
        self.players.dereference( nick )

        self.host.leaveGame( nick, self )
        
        if nick in self.people:
            del self.people[ self.people.index(nick) ]
            
        self.host.UpdateGame(self.channel,len(self.people))

        if len(self.people) == 0:
            self.SetTopic( "CRY_WOLF: Closing empty room..." )
            self.Timer = self.DieOnEmpty
            self.Overflow = 15
            self.gameStart = False
            self.gameOver = False
            return
        
        if self.gameStarted and not self.gameOver:
            self.players.abandon( nick )
            self.eliminated.append( nick )
            if nick in self.liveSheep:
                del self.liveSheep[ self.liveSheep.index(nick) ]
            elif nick in self.liveWolves:
                del self.liveWolves[ self.liveWolves.index(nick) ]
            self.Notice( self.channel, 'Well, %s has ran out of the hunt! Better hope he was not on your team!' % (nick) )
        else:
            waitingOn = self.minPlayers - len(self.people)

            if waitingOn > 0:
                self.Topic( 'CRY_WOLF: Waiting for %i players' % (waitingOn) )
                self.Timer = None

    def names( self, nicks ):
        if len( nicks ) > 1:
            self.host.MakeGame()
            self.Part()
        else:
            creator = self.host.FetchGame(self)
            
            self.host.ActiveGame( self.channel, self.minPlayers, self.maxPlayers )
            self.Mode( ['+sntil', str(self.maxPlayers + 1)] )
            self.Invite( creator )

    def StartGame( self ):
        self.host.DeactiveGame( self.channel )
        self.gameStarted = True

        self.sheep  = self.people[:]
        self.wolves = []
        self.rounds = 1

        wolfCount = (len(self.people) - 4)/3

        for i in range(wolfCount):
            self.wolves.append( self.sheep.pop( randint(0,len(self.sheep)-1) ) )
       
        self.liveWolves = self.wolves[:]
        self.liveSheep  = self.sheep[:]

        self.Timer = self.SuspicionsMode
        self.Overflow = self.delibTime
        
        wolves = ""
        
        for player in self.people:
            self.Notice( player, gameStartMsg )

        for player in self.wolves:
            wolves = wolves + player + ","
        wolves = wolves[:-1]

        self.Notice( wolves, wolfMsg % (wolves) )

        for player in self.sheep:
            self.Notice( player, sheepMsg % (wolfCount) )

        whispers = self.sheep[:]
        safe = []

        self.SetTopic("CRY_WOLF: After-noon (Select 1 player for elimination)")

        for i in range( randint(4,len(self.sheep)-1) ):
            whispers.pop( randint(0,len(whispers)-1) )

        for i in range( randint(1,wolfCount+1) ):
            safe.append( self.sheep[randint(0,len(self.sheep)-1)] )

        while len(whispers) > 0:            
            self.Notice( whispers.pop(), "You can trust %s." % (safe[randint(0,len(safe)-1)]) )

    def vote( self, source, targets ):
        source = source
        
        if source in self.eliminated:
            self.Notice( source, "You cannot vote, you've been eliminated" )
            return
        elif self.Timer == self.KillingMode and not source in self.wolves:
            self.Notice( source, "You cannot murder, you're not a wolf" )
            return
        elif self.Timer == self.OustingMode and source in self.options:
            self.Notice( source, "You cannot vote if you are up on the block!" )
            return

        if self.Timer == self.OustingMode:
            # Only one may be eliminated
            targets = targets[:1]
        else:
            # Clip to round
            targets = targets[:self.rounds]        

        for i in range(len(targets)):
            targets[i] = targets[i]

        for targ in targets:
            targ = targ
            if targ == source:
                self.Notice( source, "You cannot vote for yourself!" )
            elif targ in chose:                
                self.Notice( source, "You cannot vote on %s twice!" % (targ) )
            elif targ in self.eliminated:
                self.Notice( source, "You cannot vote on %s, they're elimiated!" % (targ) )
            elif targ not in self.people:
                self.Notice( source, "Who is %s?  Are you feeling alright?" % (targ) )
            elif self.Timer == self.KillingMode and targ not in self.sheep:
                self.Notice( source, "What are you thinking? %s is a wolf!" % (targ) ) 
            elif self.Timer == self.OustingMode and targ not in self.options:
                self.Notice( source, "Crafty man, %s is not up for ousting!" % (targ) )
            else:
                chose.append( targ )
                continue
            return
        
        # --- Check for duplicate votes ---
        if source in self.votes and self.votes[source] == targets:
            self.Notice( source, "You already cast that vote!" )
            return

        # --- Update suspicion level ---
        if source in self.votes:
            notifys = self.votes[source] + targets
        else:
            notifys = targets[:]
            
        self.votes[source] = targets

        options = {}
        for player in self.people:
            options[player] = []
        for key in self.votes:
            for o in self.votes[key]:
                options[o].append(key)
        totalVoters = len(self.liveSheep + self.liveWolves)

        if self.Timer != self.KillingMode:           
            for targ in notifys:
                if notifys.count(targ) == 1:
                    self.Notice( targ, "Your suspicion level changed to %i/%i" % (len(options[targ]),totalVoters) )

            for wolf in self.liveWolves:
                if len(options[wolf]) >= 3:
                    enemies = ""
                    for enemy in options[wolf]:
                        enemies += "%s, " % (enemy)
                    enemies = enemies[:-2]
                    
                    self.Notice( targ, "You have developed quite a few enemies... %s" % (enemies) )

        # --- Display who they are voting for

        display = ""
        for targ in targets:
            display += "%s, " % (targ)
        self.Notice( source, "Voting for: %s" % (display[:-2]) )
            
    def TabulateVotes( self ):
        options = {}

        for player in self.people:
            options[player] = []
        
        if self.Timer == self.OustingMode:
            if randint(0, 1) == 0:
                best1, best2 = self.options[0], self.options[1]
            else:
                best1, best2 = self.options[1], self.options[0]
        elif self.Timer == self.KillingMode:
            best1, best2 = self.liveSheep[randint(0,len(self.liveSheep)-1)], None
        else:
            opt = self.liveSheep + self.liveWolves   
            best1 = opt[randint(0,len(opt)-1)]
            best2 = opt[randint(0,len(opt)-1)]

        for key in self.votes:
            for o in self.votes[key]:
                options[o].append(key)

        for key in options:
            if best1 == None or len(options[key]) >= len(options[best1]):
                best2, best1 = best1, key
            elif best2 == None or len(options[key]) >= len(options[best2]):
                best2 = key

        if self.Timer == self.OustingMode:
            votes = ""
            for name in options[best1]:
                votes += "%s, " % (name)
            self.Notice( self.channel, "Voters for %s: %s" % (best1, votes[:-2]) )

            if best1 in self.liveSheep:
                self.oustedSheep[best1] = options[best1]

            votes = ""
            for name in options[best2]:
                votes += "%s, " % (name)
            self.Notice( self.channel, "Voters for %s: %s" % (best2, votes[:-2]) )

        self.votes = {}

        return best1, best2

    def SuspicionsMode( self ):
        best1, best2 = self.TabulateVotes()
        self.options = [best1, best2]

        self.Notice( self.channel, "You have selected %s and %s for elimiations... please vote on your choice" % (best1, best2) )
        
        self.SetTopic("CRY_WOLF: Dusk (Select %s or %s for elimination)" % (best1,best2))
        self.Timer = self.OustingMode
        self.Overflow = self.voteTime

    def OustingMode( self ):
        best1, best2 = self.TabulateVotes()
        self.Notice( self.channel, "You have chosen %s to be removed from the group... hope you chose wisely" % (best1) )
        self.eliminated.append( best1 )
        self.Mode( ['-v', best1] )

        if best1 in self.liveSheep:
            del self.liveSheep[ self.liveSheep.index(best1) ]
        else:
            del self.liveWolves[ self.liveWolves.index(best1) ]
        
        if len(self.liveWolves) == 0:            
            self.Timer = None
            self.players.score( winners = self.sheep, losers = self.wolves )
            self.Notice( self.channel, "Congradulations sheep!  The wolves have all been caught" )
            self.GameOver()
            return
        if len(self.liveWolves) >= len(self.liveSheep):
            self.Timer = None
            self.players.score( winners = self.wolves, losers = self.sheep )
            self.Notice( self.channel, "Congradulations wolves!  You will feast on your victims tonight!" )
            self.GameOver()
            return
        else:        
            self.Timer = self.KillingMode
            self.Overflow = self.killTime

        self.SetTopic("CRY_WOLF: Evening... Someone will die...")

        wolves = ""        
        for player in self.wolves:
            wolves = wolves + player + ","
        wolves = wolves[:-1]

        self.Notice( wolves, huntMsg )

        for player in self.liveSheep:
            self.Notice( player, sleepMsg )

        dreaming = self.sheep[:]

        for i in range( randint(2,len(dreaming)) ):
            dreaming.pop( randint(0,len(dreaming)-1) )

        for player in dreaming:
            if randint( 0, 9 ) == 0:    # 10% change of getting a believe statement
                believe = self.liveSheep[ randint(0,len(self.liveSheep)-1) ]
                self.Notice( player, believeState[ randint(0,len(believeState)-1) ] % believe )
            else:                       # 90% chance of getting a 3 set do-not-believe
                wolf = self.liveWolves[ randint(0,len(self.liveWolves)-1) ]
                sheep1 = self.liveSheep[ randint(0,len(self.liveSheep)-1) ]
                sheep2 = self.liveSheep[ randint(0,len(self.liveSheep)-1) ]

                while sheep1 == sheep2:
                   sheep2 = self.liveSheep[ randint(0,len(self.liveSheep)-1) ]
                
                order = randint(1,3)

                if order == 1:
                    notrust = wolf, sheep1, sheep2
                elif order == 2:
                    notrust = sheep1, wolf, sheep2
                else:
                    notrust = sheep1, sheep2, wolf
            
                self.Notice( player, noTrustState[ randint(0,len(believeState)-1) ] % notrust[0] )
                self.Notice( player, noTrustState[ randint(0,len(believeState)-1) ] % notrust[1] )
                self.Notice( player, noTrustState[ randint(0,len(believeState)-1) ] % notrust[2] )
        
    def KillingMode( self ):
        if self.rounds < 3:
            self.rounds = self.rounds + 1

        best1, best2 = self.TabulateVotes()
        self.eliminated.append( best1 )
        self.Mode( ['-v', best1] )
        del self.liveSheep[self.liveSheep.index(best1)]

        if len(self.liveWolves) == 0:            
            self.Timer = None
            self.players.score( winners = self.sheep, losers = self.wolves )
            self.Notice( self.channel, "Congradulations sheep!  The wolves have all been caught" )
            self.GameOver()
            return
        elif len(self.liveWolves) >= len(self.liveSheep):
            self.Timer = None
            self.players.score( winners = self.wolves, losers = self.sheep )
            self.Notice( self.channel, "Congradulations wolves!  You will feast on your victims tonight!" )
            self.GameOver()
            return
        else:
            self.Notice( self.channel, "%s was killed! Who shall be next?" % (best1) )
            mode = randint(0,6)
            if mode == 0:   # X wolves remain
                self.Overflow = self.delibTime * 0.5
                self.Timer    = self.WolveRemain
            elif mode == 1: # X was NOT a wolf!
                self.Overflow = self.delibTime * 0.5
                self.Timer    = self.NotAWolf
            else:
                self.Timer = self.SuspicionsMode
                self.Overflow = self.delibTime 

        self.SetTopic("CRY_WOLF: After-noon (Choose %i players for elimination)" % (self.rounds))

        for player in self.liveSheep:
            self.Notice( player, 'You survived the night... how long will it last?' )

    def WolveRemain( self ):
        self.Notice( self.channel, "Now is not the time to feel safe, %i wolves still remain!" % (len(self.liveWolves)) )
        self.Timer = self.SuspicionsMode
        self.Overflow = self.delibTime / 2

    def NotAWolf( self ):
        badChoises = len( self.oustedSheep )
        if badChoises > 0:
            if badChoises == 1:
                nick = self.oustedSheep[0]
            else:
                nick = self.oustedSheep[randint(0,badChoises-1)]
            self.Notice( self.channel, "I hope you're all happy, %s was NOT a wolf!" % (nick) )
        
        self.Timer = self.SuspicionsMode
        self.Overflow = self.delibTime / 2
        
    def GameOver( self ):
        message = "Wolves: "

        for player in self.wolves:
            if player in self.eliminated:
                message += "*"
            message += player + " (%iw/%il/%ia)  " % self.players.getScore( player )

        message += "\nSheep: "

        for player in self.sheep:
            if player in self.eliminated:
                message += "*"
            message += player + " (%iw/%il/%ia)  " % self.players.getScore( player )
        

        message += "\n* Player was eliminated\nEveryone is welcome to stay and chat, but this game is over"

        self.Notice( self.channel, message )
            
        self.Part()
        self.close()    # For shitty servers that don't send a self-part

    def message( self, source, message ):
        # ---- Should keep track of flooding here... ---
        pass

    def mode( self, args ):
        pass

    def DieOnEmpty( self ):
        self.Part()
        self.Timer = None

    def Tick( self, ticks ):
        if self.Timer == None:
            return

        self.Overflow = self.Overflow - ticks

        units = int(round(self.Overflow / 15))

        if units > 3:
            units = units & 0xFFFFFFFC

        if units != self.TopicCount: # if
            self.TopicCount = units
            mn = units / 4
            sec = (units % 4) * 15
            if mn != 0:
                self.Topic( "%s (%im %isec)" % ( self.TopicTemp, mn, sec ) )
            elif sec != 0:
                self.Topic( "%s (%isec)" % ( self.TopicTemp, sec ) )
            else:
                self.Topic( "%s" % ( self.TopicTemp ) )

        if self.Overflow < 0:
            self.Timer()
        
    def wolfChat( self, source, message ):
        source = source
        if self.gameStarted and source in self.wolves and len(self.wolves) >= 2:
            dest = ""

            for wolf in wolves:
                if wolf != source:
                    dest += "%s," % (wolf)
            
            self.host.cmd( 'PRIVMSG %s :--%s-- %s' % ( dest, source, message ) )

# ---- CASE SENSITIVITY HERE DOWN! -------------------------

class CryWolf(irc.IRC):
    def __init__( self, server, port, nick, altnick, channel ):
        self.nick = nick

        self.lobby = channel
            
        if altnick.find("%") >= 0:
            self.alt_nick = []
            for i in range(64):
                self.alt_nick.append( altnick % (makeHashString(4)) )
        else:
            self.alt_nick = [altnick]

        self.players = players.Players()
        self.channels = {}
        self.gamesWaiting = []
        self.activeGames = {}
        self.playing = {}

        irc.IRC.__init__( self, server, port )
    
    def Private( self, source, message ):
        nick = source[:source.find("!")]

        # Server notices should be ignored
        if source.find("!") < 0:
           return
        
        if message[0] != "#":
            if nick in self.playing:
                self.playing[nick].wolfChat( nick, message )            
            return

        args = message[1:].split(" ")
        command = args[0]
        args = args[1:]

        admin = self.players.isAdmin( nick )
        login = self.players.loggedIn( nick )

        if command == "register":
            if len(args) < 1:
                self.cmd( 'PRIVMSG %s :You must specify a password to register' % (nick) )
            else:            
                success = self.players.register( source, args[0] )

                if success:
                    self.cmd( 'PRIVMSG %s :Successfully registered! Have fun playing!' % (nick) )
                else:
                    self.cmd( 'PRIVMSG %s :Either you are registered, or you are not in the channel!' % (nick) )
        elif command == "seen":
            if len(args) < 1:
                self.cmd( 'PRIVMSG %s :You must specify a player to lookup' % (nick) )
            else:
                value = self.players.getLastLogin(args[0])
                if value != None:
                    self.cmd( 'NOTICE %s :Last seen: %s' % (nick,value) )
                else:
                    self.cmd( 'NOTICE %s :Player is not registered' % (nick) )
        elif command == "rank":
            if len(args) < 1:
                self.cmd( 'PRIVMSG %s :You must specify a player to lookup' % (nick) )
            else:
                value = self.players.getRank(args[0])
                if value != None:
                    self.cmd( 'NOTICE %s :Player rank: %3.2f' % (nick,value) )
                else:
                    self.cmd( 'NOTICE %s :Player is not registered' % (nick) )
        elif command == "help":
            if len(args) < 1:
                message = helpsys.topics['help']                
            elif not args[0] in helpsys.topics:
                message = helpsys.topics['help']
            else:
                topic = args[0]
                message = helpsys.topics[topic]

            for msg in message.split("\n"):
                self.cmd( 'NOTICE %s :%s' % (nick,msg) )                            
        elif command == "login":
            if len(args) < 1:
                self.cmd( 'PRIVMSG %s :You must specify a password to login manually' % (nick) )
            else:
                error = self.players.login( source, args[0] )
                if error:
                    self.cmd( 'PRIVMSG %s :Login failed, %s' % (nick,error) )
                else:
                    self.cmd( 'PRIVMSG %s :Welcome back.  The wolves are out...' % (nick) )

                if self.players.isAdmin( nick ):
                    self.cmd( 'MODE %s +o %s' % (self.lobby, nick) )        

        elif command == "vote":
            if not nick in self.playing:
                self.cmd( "PRIVMSG %s :You can't vote if you're not playing!" % (nick) )
            elif len(args) < 1:
                self.cmd( 'PRIVMSG %s :You must choose who to vote for' % (nick) )
            else:            
                self.playing[nick].vote( nick, args )

        elif command == "create":
            if nick in self.playing:
                self.cmd( "PRIVMSG %s :One game at a time please..." % (nick) )
            elif not login:
                self.cmd( "PRIVMSG %s :You have to login to play!" % (nick) )
            elif len(args) < 2:
                self.cmd( "PRIVMSG %s :Not enough arguements to start a game..." % (nick) )
            else:
                try:
                    minplay = int(args[0])
                    maxplay = int(args[1])

                    if len(args) >= 5:
                        delib = float(args[2]) * 60
                        vote = float(args[3]) * 60
                        kill = float(args[4]) * 60
                    else:
                        delib = 180
                        vote = 60
                        kill = 120

                    if delib < 30:
                        delib = 30
                    if vote < 30:
                        vote = 30
                    if kill < 30:
                        kill = 30
                except:
                    self.cmd( "PRIVMSG %s :Bad arguements, try giving me numbers" % (nick) )
                    return

                if maxplay < minplay:
                    minplay,maxplay = maxplay,minplay

                if maxplay > 15 or minplay < 7:
                    self.cmd( "PRIVMSG %s :You MUST spectify a range between 7 to 15 players" % (nick) )
                    return

                self.QueueGame( nick, minplay, maxplay, delib, vote, kill )

        elif command == "join":
            if nick in self.playing:
                self.cmd( "PRIVMSG %s :One game at a time please..." % (nick) )
            elif not login:
                self.cmd( "PRIVMSG %s :You have to login to play!" % (nick) )
            elif len(args) < 1:
                self.cmd( "PRIVMSG %s :You should specify a game!" % (nick) )                    
            else:
                try:
                    game = int(args[0]) - 1
                except:
                    game = -1
                keys = self.activeGames.keys()

                if game < 0 or game >= len(keys):
                    self.cmd( "PRIVMSG %s :That is not a valid game." % (nick) )
                else:
                    self.cmd( "INVITE %s %s" % (nick, keys[game]) )

        elif command == "list" and login:
            if len( self.activeGames ) > 0:
                self.cmd( 'PRIVMSG %s :--- Available games ------' % (nick) )
                i = 1
                for game in self.activeGames:
                    settings = self.activeGames[game]
                    limits = settings['limits']
                    players = settings['players']
                    self.cmd( 'PRIVMSG %s :%3i) %i players (%i/%i)' % (nick, i, players, limits[0], limits[1]) )
                    i = i + 1
            else:
                self.cmd( 'PRIVMSG %s :There are no active games! Create one!' % (nick) )                
        elif command == "write" and admin:
            self.players.write()
            self.cmd( 'PRIVMSG %s :Preserved current user state' % (nick) )
        elif command == "shutdown" and admin:
            self.cmd( 'PRIVMSG %s :Shutting down...' % (nick) )
            self.cmd( 'QUIT :Administrator %s requested shutdown' % (nick) )
        else:
            self.cmd( 'PRIVMSG %s :Unknown command #%s' % (nick, command) )

    def enterGame( self, nick, game ):
        nick = nick
        if not self.inGame( nick ):
            self.playing[nick] = game
        
    def leaveGame( self, nick, game ):
        nick = nick
        if self.inGame( nick) and self.playing[nick] == game:
            del self.playing[ nick ]

    def inGame( self, nick ):
        nick = nick
        return nick in self.playing

    def ActiveGame( self, channel, minPlayers, maxPlayers ):
        self.activeGames[channel] = {
              'limits' : (minPlayers, maxPlayers),
              'players' : 0 }              

    def DeactiveGame( self, channel ):
        channel = channel
        if channel in self.activeGames:
            del self.activeGames[channel]

    def UpdateGame( self, channel, players ):
        channel = channel
        if channel in self.activeGames:
            self.activeGames[channel]['players'] = players

    def QueueGame( self, creator, minPlay, maxPlay, delTime, voteTime, killTime ):
        self.gamesWaiting.append( (creator, minPlay, maxPlay, delTime, voteTime, killTime) )
        self.MakeGame()

    def MakeGame( self ):
        if len( self.gamesWaiting ) <= 0:
            return
        
        self.cmd( 'JOIN #%s' % (makeHashString(10)) )

    def FetchGame( self, targ ):
        gameData = self.gamesWaiting.pop(0)
        creator = gameData[0]
        targ.minPlayers = gameData[1]
        targ.maxPlayers = gameData[2]
        targ.delibTime = gameData[3]
        targ.voteTime = gameData[4]
        targ.killTime = gameData[5]
        return creator
    
    def Topic( self, nick, channel, topic ):
        print "%s set topic for channel %s: %s" % (nick,channel,topic)

    def Kicked( self, source, target, channel, message ):
        channel = channel
        target = target
        
        if target == self.nick:
            self.channels[channel].close()
            del self.channels[channel]
        else:
            self.channels[channel].part(target)
        
        print "%s kicked %s from %s (%s)" % (source, target, channel, message)
            
    def Message( self, source, dest, message ):
        dest = dest
        source = source
        
        # Ignore messages from myself
        if source[:source.find("!")] == self.nick:
            return
        
        if dest[0] == "#":
            if source[:source.find("!")] != self.nick:
                self.channels[dest].message( source, message )
        else:
            self.Private( source, message )
            return
        
        print "<%s:%s> %s" % (dest, source, message)

                
    def Notice( self, source, dest, message ):
        source = source
        dest = dest

        # Ignore messages from myself
        if source[:source.find("!")] == self.nick:
            return

        if dest[0] == "#":
            if source[:source.find("!")] != self.nick:
                self.channels[dest].message( source, message )
        elif dest == self.nick:
            self.Private( source, message )
            return

        print "-%s:%s- %s" % (dest, source, message)
        
    def Error( self, message ):
        print "!!!", message

    def Mode( self, source, target, arguements ):
        target = target
        print "%s set mode %s:" % (source, target),
        for arg in arguements:
            print arg,
        print

        if target[0] == "#":
            self.channels[target].mode( arguements )

    def Names( self, channel, nicks ):
        print "Current people in %s:" % (channel),
        for nick in nicks:
            print nick,
        print

        try:
            self.channels[channel].names( nicks )
        except:
            pass

    def Quit( self, nick, reason ):
        nick = nick[:nick.find("!")]
        print "%s quit IRC" % (nick)
        for channel in self.channels:
            self.channels[channel].part(nick)

    def Parted( self, channel, nick ):
        nick = nick
        channel = channel
        
        if nick == self.nick:
            self.channels[channel].close()
            del self.channels[channel]
            print "Leaving channel", nick
        else:
            self.channels[channel].part( nick )
            print "%s parted channel %s" % (nick, channel)
    
    def Joined( self, channel, nick ):
        channel = channel
        nick = nick
        
        if nick[:nick.find('!')] == self.nick:
            if channel == self.lobby:
                construct = Lobby
            else:
                construct = GameControl

            self.channels[channel] = construct( self, channel, self.nick, self.players )
#           self.cmd( 'NAMES %s' % ( channel ) ) 
            print "Entering channel", channel
        else:
            self.channels[channel].join( nick )
            print "%s joined channel %s" % (nick, channel)
            
    def ServerMessage( self, message ):
        print message

    def UserHost( self, target, mask ):
        print "%s has a host mask of: %s" % (target, mask)

    def NickTaken( self, nick ):
        print "Nickname %s is taken" % (nick)

        if len(self.alt_nick) > 0:
            self.nick = self.alt_nick.pop()
            self.cmd( 'NICK %s' % (self.nick) )

    def NickChange( self, old, nick ):
        old = old[:old.find("!")]
        
        print "%s is now known as %s" % (old,nick)

        if self.nick == old:
            self.nick = nick
        else:
            for channel in self.channels:
                self.channels[channel].nick( old, nick )

    def Tick( self, ticks ):
        for chan in self.channels:            
            self.channels[chan].Tick( ticks )
    
    def Login( self ):
        self.cmd( 'NICK %s' % (self.nick) )
        self.cmd( 'USER %s "%s" "%s" :CRY_WOLF Game Bot' % (self.nick, socket.gethostname(), self.server) )

    def Connected( self ):
        self.cmd( "USERHOST :%s" % (self.nick) )
        self.cmd( 'JOIN %s' % (self.lobby) )
        del self.alt_nick
        
