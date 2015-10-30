from random import *
import androidhelper as android

def genroom():
    if random()<0.67:
        return 0
    else:
        return choice([1,2,3])

def movesouth():
    nm=rooms[diameter:]
    nr=[genroom() for r in range (diameter)]
    nm.extend(nr)
    return nm

def movenorth():
    nr=[genroom() for r in range (diameter)]
    nm=rooms[:len(rooms)-diameter]
    nr.extend(nm)
    return nr

def movewest():
    nm=[]
    for r in range(len(rooms)):
        if (r % diameter < diameter-1):
            if (r % diameter == 0):
                nm.append(genroom())
            nm.append(rooms[r])
    return nm

def moveeast():
    nm=[]
    for r in range(len(rooms)):
        if (r % diameter >0):
            nm.append(rooms[r])
            if (r % diameter == diameter-1):
                nm.append(genroom())
    return nm

#returns center of array of known rooms
def calcCenter():
    return int((len(rooms)-1)/2)

#returns tuple of 4 rooms adjacent to center
def getAdj():
    center=calcCenter()
    north=center-diameter
    south=center+diameter
    east=center+1
    west=center-1
    return [north,south,east,west]

#returns a string containing the known map
def getMap():
    s=""
    for r in range(len(rooms)):
        s="".join((s,str(rooms[r])))
        if (r % diameter==diameter-1):
            s="".join((s,"\n"))
    return (s)

#generates flavor text depending on event in a room
def gensmell(rm):
    if rm == 1:
        return "you hear a soft singing."
    elif rm == 2:
        return "you hear a pleasant humming."
    elif rm == 3:
        return "you hear a stifled giggle."

#confirms if anything interesting is in a room adj to center
def checksmell():
    cen=calcCenter()
    adj=getAdj()
    smelly=[rooms[n] for n in adj if rooms[n]>0]
    if smelly:
        return gensmell(choice(smelly))
    else:
        return "you hear only forlorn echoes from empty rooms."

#Resolves the events in a room based on room number
#luk changes need to be balanced to make the player capable of losing
def processRoom():
    rm=rooms[calcCenter()]
    if rm==1:
        setLuck(luk+7)
        return "You ambush an unfortunate pixie, which you swiftly pin down and devour whole. Delicious!\n\n"
    elif rm==2:
        regenMap()
        return "Before you know it, you find yourself ensnared in a warp. When you awaken your surroundings are...different.\n\n"
    elif rm==3:
        setLuck(luk-10)
        return "Something pierces you from behind! You whirl around but find nothing out of place...except your new wound.\n\n"
    elif random()<0.04:
        return "A dusty mural on the opposite wall catches your eye. You see a map!\n1=Food/2=Warp/3=Foe\n\n"+getMap()
    elif random()<0.7:
        setLuck(luk-1)
        return "The room is empty. You grimace as a little more blood trickles from your wounds.\n\n"
    else:
        return "The room is empty. %s\n\n"%(choice(ponder))

#used to regenerate the known rooms
def regenMap():
    global rooms
    rooms=[genroom() for r in range(diameter * diameter)]
    rooms[calcCenter()]=0

#after resolving the room event, generates a smell or ends game
def processTurn():
    text=processRoom()
    if luk>0:
        text="".join((text,"From the dark depths around you,\n",checksmell(),"\n\n",
        "You see four hallways around you.\nWhich will you enter?"))
    else:
        text="".join((text,"\nAt last, you fall to your knees, ",
                      "then collapse in exhaustion, unable to continue. ",
                      "\n\nThe world grows colder and the darkness closes in.\n\n",
                      "Your luck has finally run out..."))
    return text

#The loop exits because luk is <0
def closeApp():
    setLuck(-1)

#Only this method changes luk, so only need global to be in scope for this method
def setLuck(change):
    global luk
    luk=change

#Displays the title screen only
def displayStart():
    outtext="".join(("You awaken, bruised and bloodied.\n\n",
    "You are a monster, driven down from the world above.\n",
    "Your hunger for human flesh can no longer be satiated, ",
    "for you have been sealed in the Labyrinth from which none escape.\n\n",
    "However, as you lick your lips, you smell the aroma of innocent faeries, ",
    "playing obliviously, out there in the dark.\n\nTheir power will give you ",
    "the strength to escape the maze!\n\nThe hunt begins."))
    droid.dialogCreateAlert(
        "%s"%(appTitle),
        "%s"%(outtext))
    droid.dialogSetPositiveButtonText("Enter the Maze?")
    droid.dialogShow()
    response=droid.dialogGetResponse().result
    outtext=""
    droid.dialogDismiss()

#the game's main routine
#first, get a string summarizing the events in the room
#second, check if player can continue, then end game or read next movement
def displayMaze():
    global rooms
    text=processTurn()
    rooms[calcCenter()]=0

    if luk>0:
        droid.dialogCreateAlert(
            "%s"%(appTitle),
            "%s"%(text))
        droid.dialogSetPositiveButtonText("Continue...")
        droid.dialogShow()
        response=droid.dialogGetResponse().result
        droid.dialogDismiss()

        droid.makeToast("You have %d/%d luck left"%(luk,wincon))
        droid.dialogCreateAlert(
            "%s"%(appTitle),
            "%s"%(text))
        droid.dialogSetSingleChoiceItems(directions)
        droid.dialogSetPositiveButtonText("Make your choice!")
        droid.dialogSetNegativeButtonText("Succumb to death...")
        droid.dialogShow()
        response=droid.dialogGetResponse().result
        chosen=droid.dialogGetSelectedItems().result[0]
        droid.dialogDismiss()

        if "which" in response:
            result=response["which"]
            if result=="Negative":
                closeApp()
            else:
                if directions[chosen]=="North":
                    rooms=movenorth()
                elif directions[chosen]=="South":
                    rooms=movesouth()
                elif directions[chosen]=="East":
                    rooms=moveeast()
                elif directions[chosen]=="West":
                    rooms=movewest()
                else: print ("FAIL TO FIND MOVEMENT")
                
        if not 'which' in response: closeApp()
    else:
        droid.dialogCreateAlert(
            "%s"%(appTitle),
            "%s"%(text))
        droid.dialogSetPositiveButtonText("Accept your fate...")
        droid.dialogShow()
        response=droid.dialogGetResponse().result
        droid.dialogDismiss()

#Gives a victory screen if wincon is met, allowing game to end for good players
def checkWin():
    if luk>wincon:
        droid.dialogCreateAlert(
            "%s"%(appTitle),
            "%s"%(endtext))
        #droid.dialogSetPositiveButtonText("Start a new game?")
        droid.dialogSetNegativeButtonText("Accept your crown")
        droid.dialogShow()
        response=droid.dialogGetResponse().result
        droid.dialogDismiss()
        closeApp()

#call this method to run the app, contains the main loop
def runApp():
    regenMap()
    displayStart()
    while luk>0:
        displayMaze()
        checkWin()

appTitle="Minotaur Labyrinth"
directions=["North","South","East","West"]
#flavor text for empty rooms
ponder=[
    "You take a breather, licking your still-open wounds and pondering your unfortunate fate.",
    "You strain your ears, but in the silence can only make out your ragged breaths.",
    "You bellow hatred at the gods, but only the wind sighs back at you sympathetically.",
    "As you consider your next move, you unconsciously rub the broken nub of one of your horns.",
    "You can make out the faint scent of faerie dust, shaken off by its owner onto the damp stone long ago.",
    "Though all around is darkness, you still remember the first and only time you tasted sunlight.",
    "You try to remember the face of your mother. Even now, you wonder if she ever loved you.",
    "As you enter, your hooves echo against the damp stone with a clatter.",
    "You rest against the stone, remembering the hatred etched on the faces of those who exiled you.",
    "You lean against a broken column that reminds you of your original prison.",
    "You feel a strange sense of deja vu, but quickly dismiss it.",
    "You pause to contemplate your options, ignoring the emptiness in your stomach that hungers for flesh.",
    "Your surroundings are so pitch-black, you cannot tell if your eyes are open or shut.",
    "Your keen nose detects the aroma of pixies, but they have long since left this room.",
    "Though you are alone, you can still smell the blood of pixies from long ago, and your thirst grows.",
    "Unbidden, the memory of manflesh lingers on your mind, a desire you must settle for satiating with other meat."
    ]
#victory text
endtext="".join(("Thanks to the magic you absorbed from your numerous victims, ",
                  "you feel the last of your wounds closing. As you pick your ",
                  "teeth with a broken wishbone, your nose detects even more ",
                  "innocents waiting to be introduced to your stomach.\n\n",
                  "Though the hallways may be infinite, so is the food.\n\n",
                  "For the first time in a long time, you grin. Perhaps you ",
                  "feel at home in this kingdom of darkness after all..."))

prog=True
wincon=100 #luck needed to win
droid=android.Android()
luk=13 #starting luck
radius=3 #radius of dungeon stored in memory
diameter=2*radius+1
rooms=[] #global holding the stored map

runApp()
