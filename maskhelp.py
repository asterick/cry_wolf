import random

def makeMask( mask ):
    mask = mask[mask.find("!")+1:]
    loc = mask.find("@") + 1

    newMask = "*!" + mask[:loc]
    mask = mask[loc:]

    start = 0
    dots = []

    while start >= 0:
        start = mask.find(".",start+1)
        dots.append( start )

    if mask[-1] in ["0","1","2","3","4","5","6","7","8","9"]:
        if len(dots) > 3:
            dots = dots[:3]
        
        return newMask + mask[:dots[-1]] + ".*"
    else:
        if len(dots) > 3:
            dots = dots[-4:]
        return newMask + "*" + mask[dots[0]:]


def matchMask( mask, match ):
    old = 0
   
    for pattern in mask.split("*"):
        offset = match.find( pattern, old )
        old = offset + len(pattern)

        if offset < 0:
            return False
            
    return True

def makeHashString( leng = 8 ):
    string = ""

    for r in range(leng):
        string += chr(random.randint(ord('a'),ord('z')))

    return string

