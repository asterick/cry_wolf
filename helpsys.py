helpDefault = """--- \002CRY_WOLF\002:  topic (\002HELP\002) ------------
Note ALL commands are prefixed by a pound (#) sign.
Available Topics:
\002HELP    HOWTO   REGISTER    LOGIN
\002CREATE  LIST    JOIN        SHUTDOWN
\002WRITE   VOTE    SEEN        RANK
\002RULES"""

helpGameplay = """--- \002CRY_WOLF\002:  topic (\002HOWTO\002) ------------
Welcome to CRY_WOLF!  This game is similiar to that of
\002Mafia\002 or \002Werewolf\002 for those aquainted to the
game.  This is a fast-pased game, involving subversion of
trust, acquisition of loyalty... and murder.  It pits 2
un-evenly informed teams against each other in a battle for
survival.
After you register, you must then either CREATE a room or
JOIN an existing one.  Farther help on these topics are
available in their respective areas.
The game operates in 3 stages.  Afternoon, Dusk, and Evening.
Each round consists of one command, #VOTE which should be
messaged to the game controller (cry_wolf)
\002Afternoon:\002 You must select between 1-3 players to be put up for elimination.
\002Dusk:\002 Select which of the two players you ACTUALLY want to eliminate
\002Evening:\002 The wolves select a player to kill.
If you are a wolf, anything you /msg to cry_wolf that is not a command,
will automatically be forwarded to the other wolves, so you can speak
as a group without having to worry about suspicions!
Just remember, lie to your friends, destroy your enemies, survive the night."""

helpRules = """--- \002CRY_WOLF\002:  topic (\002RULES\002) ------------
\0021:\002 No ass-hattery.  If you want to anger someone, don't.
\0022:\002 NO nick-changes mid-game.  This complicates things, and will be considered quitting mid-game
\0023:\002 No Ban evasion
\0024:\002 No Flooding
\0025:\002 Please refrain from saying 'I'm a sheep!', It does no good.
\0026:\002 Use common sense.  If you think it's wrong, it probably is."""

helpRegister = """--- \002CRY_WOLF\002:  topic (\002REGISTER\002) ------------
This command creates login and rank information for you on
the bot.  Most of the time, you will not need to know your
login information, unless you are in the lobby when the bot
restarts, or you play on a different machine.  You are
required to register in order to play.
Example: \002/msg cry_wolf #REGISTER 12345"""

helpLogin = """--- \002CRY_WOLF\002:  topic (\002LOGIN\002) ------------
Resends your login information, if you are not automatically
identified, or you are an administrator, you must login
in order to play.
Example: \002/msg cry_wolf #LOGIN 12345"""

helpCreate = """--- \002CRY_WOLF\002:  topic (\002CREATE\002) ------------
Requests the creation of a game.  You must specify range that
is inside 7 to 15 players, if you are not currently in a game,
it will create a game for you.
\002Delib:\002 How much time to spend discussing who shall be voted out
\002Oust:\002 How much time to select who you want to bout out
\002Kill:\002 How much time to give the wolves to pick a victim
Format: \002/msg cry_wolf #CREATE <min> <max> <delib> <oust> <kill>
Example: \002/msg cry_wolf #CREATE 7 15"""

helpList = """--- \002CRY_WOLF\002:  topic (\002LIST\002) ------------
Requests a listing of waiting games to join."""

helpJoin = """--- \002CRY_WOLF\002:  topic (\002JOIN\002) ------------
Requests that the bot invite you to a game.
Format: \002/msg cry_wolf #JOIN 1"""

helpShutdown = """--- \002CRY_WOLF\002:  topic (\002SHUTDOWN\002) ------------
\002Only available to administrators
This causes the bot to shutdown, and log off"""

helpWrite = """--- \002CRY_WOLF\002:  topic (\002WRITE\002) ------------
\002Only available to administrators
This command will cause the server to preserve
the current user state to file, and continue gameplay.
This is a last chance precaution for crashs."""

helpVote = """--- \002CRY_WOLF\002:  topic (\002 VOTE\002) ------------
This command selects a player for either elimination.
Format: \002/msg cry_wolf #VOTE nick1 nick2 nick3
The command only uses any many votes as it needs."""

helpSeen = """--- \002CRY_WOLF\002:  topic (\002SEEN\002) ------------
This command displays the last login time for this player.
Format: \002/msg cry_wolf #SEEN nick1"""

helpRank = """--- \002CRY_WOLF\002:  topic (\002RANK\002) ------------
This command displays a numeric rank value.  It is a
calculated value and now their raw gameplay stats.  To
recieve those statistic, you must play with them.
Format: \002/msg cry_wolf #RANK nick1"""


topics = {
    'help':     helpDefault,
    'howto':    helpGameplay,
    'register': helpRegister,
    'login':    helpLogin,
    'create':   helpCreate,
    'list':     helpList,
    'join':     helpJoin,
    'shutdown': helpShutdown,
    'write':    helpWrite,
    'vote':     helpVote,
    'seen':     helpSeen,
    'rank':     helpRank,
    'rules':    helpRules,
}

