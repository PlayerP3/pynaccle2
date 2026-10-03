import pygame,os,json,ast,sys
from .screen import gameScreen
# from .objectsystem import objectManager

class Tilemap():
    def __init__(self):


        self.accessible_tiles = []
        self.inaccessible_tiles = []
        self.tilemap = {}
        self.astar_graph = {}

        # chunk vars
        self.currentChunk = "0"
        self.openChunks = ["0"]
        self.chunksInFrame = ["0"]

        # chunk no and the objs that are in it
        self.chunkObj = {}
        self.inactiveObjs = []

    def load_tilemap(self,tileampJSONDir:str,classMappings:dict):

        # list jsons in tilemap json dir
        chunks = os.listdir(tileampJSONDir)

        for c in chunks:

            # load chunk json
            with open(f"{tileampJSONDir}/{c}", 'r') as f:
                
                params = json.load(f)

            # get chunk
            chunk = c.rstrip('.json')

            # get chunk number
            chunkNo = chunk.lstrip('chunk')

            # add chunk to tilemap
            if chunkNo not in self.tilemap:
                self.tilemap[chunkNo] = {}
                self.chunkObj[chunkNo] = []
        

            # add window for chunk
            # set chunk in bg surf
            gameScreen.add_window(chunk,width=12000,height=12000,pos=(gameScreen.fullscreen_width//2,gameScreen.fullscreen_height//2),zoom=1)
            gameScreen.windows[chunk].bg_offset_x = (gameScreen.windows[chunk].win_width)//2
            gameScreen.windows[chunk].bg_offset_y = (gameScreen.windows[chunk].win_height)//2


            # store all pos and layers
            layerPos = []

            # store layer and pos as kv pair
            for layer,layerData in params[chunkNo].items():

                for pos,metadata in layerData.items():

                    layerPos.append((layer,pos))

            # go through kv pair and remove animated sprite class and ad vars you want
            for lp in layerPos:

                buildJSON = {}

                layer = lp[0]
                pos = lp[1]

                # # get wallss change later
                # if params[chunkNo][layer][pos]['AnimatedSprite']['img_path'].split('/')[-1] == 'Wall.png':
                #     params[chunkNo][layer][pos]['class'] = 'Wall'


                # get class to convert to
                className = params[chunkNo][layer][pos]['class']
                classConversion = params[chunkNo][layer][pos]['class']
                del params[chunkNo][layer][pos]['class']

                # get obj attributes
                objinit = params[chunkNo][layer][pos]

                buildJSON.update(objinit['AnimatedSprite'])
                del objinit['AnimatedSprite']
                buildJSON.update(objinit)

                # add variables of interest from the animated sprite class, can actuall use getattr to be more efficient and have a list of vars you want
                # if "spawnOffsetX" not in buildJSON:
                #     buildJSON["spawnOffsetX"] = 16
                #     buildJSON["spawnOffsetY"] = 16

                # init obj absed on its class and set attrs
                newObj = classMappings[classConversion]()
                for att,val in buildJSON.items():
                    setattr(newObj,att,val)

                # sprite.surface_to_draw_on = 'tilemap'
                # sprite.vertice = 'topleft'

                # set new vars
                newObj.vertice = 'center'
                newObj.zlayer_drawing = int(layer)
                newObj.spawnLocation = ast.literal_eval(pos)
                newObj.connectedChunk = chunkNo

                # start building copy
                if layer not in self.tilemap[chunkNo]:
                    self.tilemap[chunkNo][layer] = {} 
                
                if pos not in self.tilemap[chunkNo][layer]:
                    self.tilemap[chunkNo][layer][pos] = {}

                # add animated sprite info to myCopy
                self.tilemap[chunkNo][layer][pos] = newObj

                
                # determine what happens to different objs
                # newObj.hurtbox.topleft = ast.literal_eval(pos)
                # all bg tiles are drawn at the topleft vertice
                if className == 'BgTile':

                    newObj.surface_to_draw_on = chunk
                    newObj.init_sprite()
                    
                    # if posss == (0,0):
                    #     continue
                    newObj.draw_surface(position=ast.literal_eval(pos),schedule_deletion=False)

                    # add to accessible tiles
                    self.accessible_tiles.append(ast.literal_eval(pos))
                
                
                # if it is not jsut an animated sprite bg tile
                else:

                    # store obj
                    self.chunkObj[chunkNo].append(newObj)
                        

            # render 
            gameScreen.windows[chunk].render_objects_cpu()
            gameScreen.windows[chunk].drawing_queue = {}

            # add sprite for chunk obj and add it to objects to blit
            chunkObj = classMappings['Chunk']()
            chunkObj.create_chunk_sprite(gameScreen.windows[chunk].win)
            self.chunkObj[chunkNo].append(chunkObj)

    # init and add a chunk
    def add_chunk(self,chunk:int):

        if chunk not in self.openChunks:
            self.openChunks.append(chunk)

            for gameobj in self.chunkObj[chunk]:
                gameobj.init()
                gameobj.spawn(pos=gameobj.spawnLocation,vertice='center')

                # if chunk then dont add accessibility
                if gameobj.__class__.__name__ == 'Chunk':
                    continue
                
                # if inaccessible then add to inaccessible tiles
                if gameobj.inaccessible:
                    self.inaccessible_tiles.append(gameobj.spawnLocation)

                elif not gameobj.inaccessible:
                    self.accessible_tiles.append(gameobj.spawnLocation)

    # return objects of certain class
    def get_obejcts(self,className:str):

        gameObjects = []

        for chunk in self.chunkObj:

            gameObjects.extend(self.chunkObj[chunk])

        gameObjects = [x for x in gameObjects if x.__class__.__name__ == className]

        return gameObjects

tilemapProcessor = Tilemap()