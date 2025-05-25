import pygame
import xmltodict
import json

pygame.init()
screen = pygame.display.set_mode((1280*1.5, 720*1.5))
clock = pygame.time.Clock()
running = True

FPS = 200
SAMPLERATE = .0005
SCALAR = 1
TRACKOFFESET = 50

trackFileName = "f1-Track-Data/greatbritain.svg"

track =  pygame.transform.scale_by(pygame.image.load(trackFileName), SCALAR)

Percent = 0 

def getPointOnTrack(percent):
    '''
    With SVG Path From the SVG using 'xmltodict'
    This returns JSON of the xml's in the file
    '''
    
    file = open(trackFileName, "r")
    filedata = "".join(file.readlines())
    file.close()
    
    trackXMLdata = xmltodict.parse(filedata)
    '''
    in the json, it's 'indented' svg->path->@d
    
    IE:
    
    {svg : {
        path: {
            @d : []
        }
        
    }}
    '''
    SVGdata = trackXMLdata["svg"]
    Pathdata =SVGdata["path"]
    fullTrackPath = ""
    Sector1Path = ""    # Not used atm
    Sector2Path = ""    # Not used atm
    Sector3Path = ""    # Not used atm
    
    for path in Pathdata:
        if path["@class"] == "st0":
            fullTrackPath = path["@d"]
        elif path["@class"] == "st1":
            Sector1Path = path["@d"]
        elif path["@class"] == "st2":
            Sector2Path = path["@d"]
        elif path["@class"] == "st3":
            Sector3Path = path["@d"]
    
    '''
    All correct path data for full track and sectors of track
    '''
    
    '''
    convert string to list of path commands
    '''
    
    fullTrackCommands = fullTrackPath.split("C") #Forced track data be to reletive and all by C
        

    '''
    We now have the list of svg commands ie a very basic way to get 'percent' spots
    '''
    
    currentSpot = int(len(fullTrackCommands) * percent)
    #print(f'current command : "{fullTrackCommands[currentSpot]}"')
    
    '''
    convert command to points on the track
    '''
    currentCommand = fullTrackCommands[currentSpot]
    splitcommand = currentCommand.split(' ')
    #remove all letters from command
    
    PossibleLetters = ['M', 'C', 'Z', ' ', '']
    for comm in splitcommand:
        if comm in PossibleLetters:
            splitcommand.remove(comm)
    
    '''
    getting x,y from Bézier curves
    '''
    
    # so, we should get 6 points from a bezier curve command
    # splitting by ',' will sometimes give 6 unless a negitive number exists then theres no ',', just '-'
    
    # #SO
            
    helperPoints = []
    
    if len(splitcommand) == 6 and currentSpot != 0:
        currentCommand2 = fullTrackCommands[currentSpot-1]
        splitcommand2 = currentCommand2.split(' ')
        #remove all letters from command
        
        PossibleLetters = ['M', 'C', 'Z', ' ', '']
        for comm in splitcommand2:
            if comm in PossibleLetters:
                splitcommand2.remove(comm)
                
        previousY = splitcommand2[-1]
        previousX = splitcommand2[-2]
        
        p = [
            [float(previousX), float(previousY)],
            [float(splitcommand[0]), float(splitcommand[1])],
            [float(splitcommand[2]), float(splitcommand[3])],
            [float(splitcommand[4]), float(splitcommand[5])]
            ]
        
        helperPoints = p
        
        # need a smoother % based on the given percent
        totalSize = 1/len(fullTrackCommands)
        percentThrough = (percent % totalSize) / totalSize
        t = percentThrough % 1
        print(f"percent t: \t {t}")
        
        # Calculate fushia point based on t - https://javascript.info/bezier-curve#maths
        
        # P = (1−t)^3P1 + 3(1−t)^2*tP2 +3(1−t)t2P3 + t3P4
        x =   (((1-t)*(1-t)*(1-t)) * p[0][0]) + (3 * ((1-t)*(1-t)) * t * p[1][0]) + (3 * (1-t) * (t*t) * p[2][0]) + (t*t*t)*p[3][0]
        
        y =   (((1-t)*(1-t)*(1-t)) * p[0][1]) + (3 * ((1-t)*(1-t)) * t * p[1][1])+ (3 * (1-t) * (t*t) * p[2][1])+ (t*t*t)*p[3][1]


    
        
    else:
        x = splitcommand[0]
        y = splitcommand[1]
    
    
    #print(",".join(splitcommand))
    
    return ((float(x)), (float(y)), helperPoints)


#http://ergast.com/mrd/ - F1 API for getting race data    

carTrace = []
carSize = 5

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if Percent > 1-SAMPLERATE:
        running = False
    
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    screen.blit(track, (TRACKOFFESET, TRACKOFFESET))
    
    x, y, points = getPointOnTrack(Percent % 1)
    
    carTrace.append([x,y])
    
    cnt = 1
    for point in points:
        pygame.draw.circle(screen, (20, 100 + 30*cnt, 20), ((point[0]*SCALAR) + TRACKOFFESET, (point[1]*SCALAR)+ TRACKOFFESET), 2)
        cnt +=1 
    
    for point in carTrace:
        pygame.draw.circle(screen, (20, 100, 100), ((point[0]*SCALAR) + TRACKOFFESET, (point[1]*SCALAR)+ TRACKOFFESET), 1)
    
    pygame.draw.circle(screen, (200, 20, 20), ((x*SCALAR)+ TRACKOFFESET, (y*SCALAR) + TRACKOFFESET), 2 * carSize)
    # RENDER YOUR GAME HERE
    
    # flip() the display to put your work on screen
    pygame.display.flip()

    Percent += SAMPLERATE
    print(f"track Percent : {Percent}")
    clock.tick(FPS)  # limits FPS to FPS const

f = open(f"NodeArray-{trackFileName.split('/')[1]}.csv", "w")
f.write('\n'.join(str(stin) for stin in carTrace))
f.close()

pygame.quit()