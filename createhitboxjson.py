import json,os,pygame
pygame.init()

myDirs = 'Sprites'

potentialDirsPath = [x[0].replace("\\",'/') for x in os.walk(myDirs)]
myDirsPath = []

# filter dirs path to only contain dirs with pngs
for d in potentialDirsPath:
    if '.png' in ''.join(os.listdir(d)):
        myDirsPath.append(d)


outJson = {}

# get pngs and create json we can edit hitboxes in 
for dd in myDirsPath:
    for png in os.listdir(dd):

        impath = f"{dd}/{png}"

        # get img path

        # load image
        image = pygame.image.load(impath)

        # get sprite width and height
        spriteName,whSprite = impath.rstrip('.png').split('_')
        spriteWidth,spriteHeight = [int(x) for x in whSprite.split('x')]

        outJson[impath] = {}

        for j in range(image.get_height()//spriteHeight):

            for i in range(image.get_width()//spriteWidth): 

                outJson[impath][str(i)] = ['0,0,32,32,0,0']



with open('configs/config_hitboxes.json','w') as f:

    json.dump(outJson, f,indent=4)


