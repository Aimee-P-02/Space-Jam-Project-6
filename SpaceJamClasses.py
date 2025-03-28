from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from CollideObjectBase import *






class Planet(SphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Planet, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 1.09)
        
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        print("node name:" + str(nodeName))
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)


class Drone(SphereCollideObject):
    
    dronecount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Drone, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.5)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        print("node name:" + str(nodeName))
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)




class Universe(InverseSphereCollideObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
       super(Universe, self).__init__(loader,modelPath, parentNode, nodeName, Vec3(0,0,0), 0.9)
       self.modelNode.setPos(posVec)
       self.modelNode.setScale(scaleVec)

       self.modelNode.setName(nodeName)
       print("node name:" + str(nodeName))
       tex = loader.loadTexture(texPath)
       self.modelNode.setTexture(tex, 1)

class SpaceStation(CapsuleCollidableObject):
    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(SpaceStation, self).__init__(loader, modelPath, parentNode, nodeName, 1, -1, 5, 1, -1, -5, 10)
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        print("node name:" + str(nodeName))
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

class Missile(SphereCollideObject):

    fireModels = {}
    cNodes = {}
    collisionSolids = {}
    Intervals = {}
    missileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 1.0):
        super(Missile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)
        self.modelNode.setName(nodeName)
        print("node name:" + str(nodeName))
        

        Missile.missileCount += 1
        Missile.fireModels[nodeName] = self.modelNode
        Missile.cNodes[nodeName] = self.collisionNode
        Missile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        Missile.cNodes[nodeName].show()
        print("fire torpedo #" + str(Missile.missileCount))

    
class LargeMissile(SphereCollideObject):

    fireModels = {}
    AltcNodes = {}
    collisionSolids = {}
    AltIntervals = {}
    LargeMissileCount = 0

    def __init__(self, loader: Loader, modelPath: str, parentNode: NodePath, nodeName: str, posVec: Vec3, scaleVec: float = 3.5):
        super(LargeMissile, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 6.0)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setPos(posVec)

        LargeMissile.LargeMissileCount += 1
        LargeMissile.fireModels[nodeName] = self.modelNode
        LargeMissile.AltcNodes[nodeName] = self.collisionNode

        # for debugging

        LargeMissile.collisionSolids[nodeName] = self.collisionNode.node().getSolid(0)
        LargeMissile.AltcNodes[nodeName].show()
        print("fire alternate torpedo #" + str(LargeMissile.LargeMissileCount))










