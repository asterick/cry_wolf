import pickle, md5, time

from maskhelp import *

class Players:
    def __init__( self, repository = "players.pkl" ):
        self.repository = repository

        try:
            fo = file( repository, "r" )
            self.players = pickle.load( fo )
            fo.close()
        except IOError:
            self.players = {}
        self.logins = []
        self.refs = []
        
    def write( self ):
        fo = file( self.repository, "w" )
        pickle.dump( self.players, fo )
        fo.close()
        
    def register( self, player, passwd, admin = False ):
        passwd = md5.md5( passwd ).digest()
        player = player

        nick = player[:player.find("!")]

        if not nick in self.refs:
            return False        

        mask = makeMask( player )

        if not nick in self.players:
            self.players[nick] = { 'masks':[mask],
                                   'passwd':passwd,
                                   'score':(0,0,0),
                                   'admin':admin,
                                   'lastlogin': time.asctime()}
            self.logins.append( nick )
            return True

        return False

    def login( self, player, passwd = None ):
        player = player
        nick = player[:player.find("!")]

        if not nick in self.refs:
            return "Player is not in a game or lobby"
        if nick in self.logins:
            return "Already logged in"
        if not nick in self.players:
            return "Not registered"

        if not passwd == None:
            passwd = md5.md5( passwd ).digest()

            if not self.players[nick]['passwd'] == passwd:
                return "Incorrect password"

            self.players[nick]['lastlogin'] = time.asctime()
            self.logins.append( nick )

            mask = makeMask( player )
            if not mask in self.players[nick]['masks']:
                self.players[nick]['masks'].append( mask )
            
            return None
        elif not self.players[nick]['admin']:
            for check in self.players[nick]['masks']:
                if matchMask( check, player ):
                    self.players[nick]['lastlogin'] = time.asctime()
                    self.logins.append( nick )
                    return None

            return "No matching masks"
        else:
            return "Cannot auto-login administrators"

    def score( self, winners, losers ):
        for player in winners:
            player = player
            w,l,a = self.players[player]['score']
            self.players[player]['score'] = (w+1,l,a)
        for player in losers:
            player = player
            w,l,a = self.players[player]['score']
            self.players[player]['score'] = (w,l+1,a)

    def abandon( self, player ):
        player = player
        w,l,a = self.players[player]['score']
        self.players[player]['score'] = (w,l,a+1)

    def promote( self, player, admin = True ):
        player = player
        self.players[player]['admin'] = admin

    def isAdmin( self, player ):
        player = player
        if not player in self.logins:
            return False
        elif not player in self.players:
            return False

        return self.players[player]['admin']

    def getScore( self, player ):
        player = player
        if not player in self.players:
            return None

        return self.players[player]['score']

    def getScore( self, player ):
        player = player
        if not player in self.players:
            return None

        return self.players[player]['score']

    def getLastLogin( self, player ):
        player = player
        if not player in self.players:
            return None

        return self.players[player]['lastlogin']

    def getRank( self, player ):
        player = player
        if not player in self.players:
            return None

        win, loss, abandon = self.players[player]['score']

        return win*2 - loss - abandon*3

    def loggedIn( self, player ):
        player = player
        return player in self.logins

    def reference( self, player ):
        player = player
        self.refs.append( player )

    def dereference( self, player ):
        player = player
        try:
            del self.refs[ self.refs.index( player ) ]
        except:
            pass
        
        if not player in self.refs:
            self.logout(player)

    def logout( self, player ):
        player = player
        try:
            index = self.logins.index( player )
            del self.logins[ index ]
        except:
            pass

        
