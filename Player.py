from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, TransparencyAttrib, CollisionTraverser, CollisionHandlerEvent, CollisionSphere
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Missile
from SpaceJamClasses import LargeMissile
from direct.gui.OnscreenImage import OnscreenImage

from direct.interval.LerpInterval import LerpFunc
from direct.particles.ParticleEffect import ParticleEffect
# Regex module import for string editing
import re



class SpaceShip(SphereCollideObject):
    def __init__(self, loader: Loader, traverser: CollisionTraverser, manager: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):

        super(SpaceShip, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0,0,0), 3)
        self.accept = accept
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)

        self.modelNode.setName(nodeName)
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)
        
        self.taskMgr = manager
        self.loader = loader

        self.render = parentNode
        self.setKeyBinding()
        self.reloadTime = .25
        self.BoostCooldownTime = .85 # boost cooldown longer than bullet reload
        self.missileDistance = 4000 # until the missile explodes
        self.missileBay = 1 # only one missile in the missile bay to be launched
        self.altMissileBay = 1 
        self.numBoosts = 1 # number of boosts availiable like with missiles

        self.altmissileDistance = 2500 # shorter distance since bullet is larger
        self.altReloadTime = .50 # longer reload time

        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34)
        self.taskMgr.add(self.CheckAltIntervals, 'checkLargeMissiles', 34)
        self.EnableHud()
        self.cntExplode = 0
        self.explodeIntervals = {}
        
        self.traverser = traverser
        self.handler = CollisionHandlerEvent()
        self.handler.addInPattern('into')
        self.accept('into', self.HandleInto)
       
        


    def Thrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyThrust,'forward-thrust')
        else:
            self.taskMgr.remove('forward-thrust')

    def applyThrust(self,task):
        rate = 5
        trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()
        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont
    
    def Boost(self, keydown):
        if keydown:
            self.taskMgr.add(self.ApplyBoost, 'accelerate')
        else:
            self.taskMgr.remove('accelerate')


    def ApplyBoost(self, task):
        if self.numBoosts == 1:
        #rate should be must faster than normal movement
            rate = 500
        # still moves ship forward just like thrust

            trajectory = self.render.getRelativeVector(self.modelNode, Vec3.forward())
            trajectory.normalize()
            self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

            self.numBoosts = self.numBoosts - 1

            return Task.done
        
        else:
            if not self.taskMgr.hasTaskNamed('cooldown'):
                print('initialize cooldown')
                self.taskMgr.doMethodLater(0, self.BoostCooldown, 'cooldown')
                return Task.cont
    
    def BoostCooldown(self, task):
        # similar to the reloading method used for the missiles

        if task.time > self.BoostCooldownTime:
            self.numBoosts += 1

            if self.numBoosts > 1:
                self.numBoosts = 1

            print('boost is ready to use')

            return Task.done
        
        elif task.time <= self.BoostCooldownTime:
            print('boost in cooldown...')

            return Task.cont




    def setKeyBinding(self):
        #all key bindings here
        self.accept('space',self.Thrust, [1])
        self.accept('space-up',self.Thrust, [0])

        self.accept('arrow_left', self.LeftTurn, [1])
        self.accept('arrow_left-up', self.LeftTurn, [0])

        self.accept('arrow_right', self.RightTurn, [1])
        self.accept('arrow_right-up', self.RightTurn, [0])

        self.accept('arrow_up', self.TurnUp, [1])
        self.accept('arrow_up-up', self.TurnUp, [0])

        self.accept('arrow_down', self.TurnDown, [1])
        self.accept('arrow_down-up', self.TurnDown, [0])

        self.accept('a', self.RollLeft, [1])
        self.accept('a-up', self.RollLeft, [0])

        self.accept('s', self.RollRight, [1])
        self.accept('s-up', self.RollRight, [0])

        self.accept('f', self.Fire)
        self.accept('l', self.AltFire)

        self.accept('shift', self.Boost, [1])
        

    def LeftTurn(self,keyDown):
        if keyDown:
            self.taskMgr.add(self.applyLeftTurn, 'left-turn')

        else:
            self.taskMgr.remove('left-turn')

    def applyLeftTurn(self, task):
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() + rate)

        return Task.cont
    # turn right
    def RightTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRightTurn, 'right-turn')

        else:
            self.taskMgr.remove('right-turn')

    def applyRightTurn(self, task):
        rate = 0.5
        self.modelNode.setH(self.modelNode.getH() - rate)

        return Task.cont



    #turn up

    def TurnUp(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyTurnUp, 'up-turn')

        else:
            self.taskMgr.remove('up-turn')

    def applyTurnUp(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() + rate)

        return Task.cont

    #turn down

    def TurnDown(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyTurnDown, 'down-turn')

        else:
            self.taskMgr.remove('down-turn')

    def applyTurnDown(self, task):
        rate = 0.5
        self.modelNode.setP(self.modelNode.getP() - rate)

        return Task.cont

    #roll right

    def RollRight(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRollRight, 'roll-right')

        else:
            self.taskMgr.remove('roll-right')

    def applyRollRight(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() - rate)

        return Task.cont

    #roll left

    def RollLeft(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.applyRollLeft, 'roll-left')

        else:
            self.taskMgr.remove('roll-left')

    def applyRollLeft(self, task):
        rate = 0.5
        self.modelNode.setR(self.modelNode.getR() + rate)

        return Task.cont
    
    def Fire(self):
        if self.missileBay:
            travRate = self.missileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) # the direction the spaceship is facing
            # normalize to avoid math mistakes
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.missileBay -= 1
            tag = 'Missile'+ str(Missile.missileCount)
            posVec = self.modelNode.getPos() + inFront # spawn missile in front of nose of ship
            currentMissile = Missile(self.loader,'./Assets/Phaser/phaser.egg', self.render, tag, posVec, 4.0)
            self.traverser.addCollider(currentMissile.collisionNode, self.handler)
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            Missile.Intervals[tag].start()
            
            

        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('initialize reload')
                self.taskMgr.doMethodLater(0, self.Reload, 'reload')
                return Task.cont
            

    def AltFire(self):
        if self.altMissileBay:
            travRate = self.altmissileDistance
            aim = self.render.getRelativeVector(self.modelNode, Vec3.forward()) # the direction the spaceship is facing
            # normalize to avoid math mistakes
            aim.normalize()
            fireSolution = aim * travRate
            inFront = aim * 150
            travVec = fireSolution + self.modelNode.getPos()
            self.altMissileBay -= 1
            tag = 'LargeMissile'+ str(LargeMissile.LargeMissileCount)
            posVec = self.modelNode.getPos() + inFront # spawn missile in front of nose of ship
            currentMissile = LargeMissile(self.loader,'./Assets/Phaser/phaser.egg', self.render, tag, posVec, 8.0)
            LargeMissile.AltIntervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1)
            LargeMissile.AltIntervals[tag].start()

            self.traverser.addCollider(currentMissile.collisionNode, self.handler)

        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('initialize reload')
                self.taskMgr.doMethodLater(0, self.AltReload, 'reload')
                return Task.cont

            

    def Reload(self, task):
        if task.time > self.reloadTime:
            self.missileBay += 1

            if self.missileBay > 1:
                self.missileBay = 1
        

            print('reload complete')

            return Task.done
        
        elif task.time <= self.reloadTime:
            print('reload proceeding...')

            return Task.cont
        

    def AltReload(self, task):
        if task.time > self.altReloadTime:
            self.altMissileBay += 1

            if self.altMissileBay > 1:
                self.altMissileBay = 1
        

            print('reload complete')

            return Task.done
        
        elif task.time <= self.altReloadTime:
            print('reload proceeding...')

            return Task.cont
        

    def CheckIntervals(self, tasK):
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()

                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]

                print(i + ' has reached the end of its fire solution')

                break
                
        return Task.cont
    

    def CheckAltIntervals(self, tasK):
        for i in LargeMissile.AltIntervals:
            if not LargeMissile.AltIntervals[i].isPlaying():
                LargeMissile.cNodes[i].detachNode()
                LargeMissile.fireModels[i].detachNode()

                del LargeMissile.AltIntervals[i]
                del LargeMissile.fireModels[i]
                del LargeMissile.cNodes[i]
                del LargeMissile.collisionSolids[i]

                print(i + ' has reached the end of its fire solution')

                break
                
        return Task.cont
    

    def EnableHud(self):
        self.Hud = OnscreenImage(image = './Assets/HUD/center.png', pos = Vec3(0,0,0), scale = 0.3)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

    def HandleInto(self, entry):

        fromNode = entry.getFromNodePath().getName()
        print("fromNode: " + fromNode)

        intoNode = entry.getIntoNodePath().getName()
        print("intoNode: " + intoNode)

        intoPosition = Vec3(entry.getSurfacePoint(self.render))
        tempVar = fromNode.split('_')

        print("tempVar: " + str(tempVar))
        shooter = tempVar[0]
        print("Shooter: " + str(shooter))
        tempVar = intoNode.split('-')
        print("tempVar1: " + str(tempVar))
        tempVar = intoNode.split('_')
        print('tempVar2: ' + str(tempVar))
        victim = tempVar[0]
        print("Victim: " + str(victim))

        strippedString = re.sub(r'[0-9]', '', victim)
       


        if('Drone' in strippedString or strippedString == 'Planet' or 'Space Station' in strippedString):
            print(victim, ' hit at ', intoPosition)
            self.DestroyObject(victim, intoPosition)
            

        if ('Drone' in strippedString or 'Planet' in strippedString or 'Space Station' in strippedString and shooter in LargeMissile.AltIntervals):
            print(victim, ' hit at ', intoPosition)
            self.DestroyObject(victim, intoPosition)
            self.setAltParticles()
            LargeMissile.AltIntervals[shooter].finish()
            
            
        if shooter in Missile.Intervals:
            Missile.Intervals[shooter].finish()

        
        print(shooter + ' is done.')
        


    def DestroyObject(self, hitID, hitPosition):
        nodeID = self.render.find(hitID)
        nodeID.detachNode()
        
        self.setParticles()

        self.explodeNode.setPos(hitPosition)
        self.Explode()
        

   

    def Explode(self):
        self.cntExplode += 1
        tag = 'particles-' + str(self.cntExplode)

        self.explodeIntervals[tag] = LerpFunc(self.ExplodeLight, duration = 4.0)
        self.explodeIntervals[tag].start()



    
    def ExplodeLight(self, t):
        if t == 1.0 and self.explodeEffect:
            self.explodeEffect.disable()

        elif t == 0:
            self.explodeEffect.start(self.explodeNode)

    
    def setParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig('./Assets/Part-Efx/basic_xpld_efx.ptf')
        self.explodeEffect.setScale(20)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')

    def setAltParticles(self):
        base.enableParticles()
        self.explodeEffect = ParticleEffect()
        self.explodeEffect.loadConfig('./Assets/Part-Efx/basic_xpld_efx.ptf')
        self.explodeEffect.setScale(40)
        self.explodeNode = self.render.attachNewNode('ExplosionEffects')

        

                
        
        

        
    


                                



