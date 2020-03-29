# Bizzaro Francesco
# March 2020
#
# This module is used to evaluate
# the maximal distance a 3D model
# can reach following a list of movements.
# It uses pybullet to simulate the physics,
# and a model from that same library.

import pybullet as p
import time
import random
import math
import numpy as np
import sys


def init_bullet(show):
    if show:
        p.connect(p.GUI)
    else:
        p.connect(p.DIRECT)
    obUids = p.loadMJCF("mjcf/humanoid.xml")
    humanoid = obUids[1]
    # gravId = p.addUserDebugParameter("gravity", -10, 10, -10)
    jointIds = []
    paramIds = []
    p.setPhysicsEngineParameter(numSolverIterations=10)
    p.changeDynamics(humanoid, -1, linearDamping=0, angularDamping=0)
    for j in range(p.getNumJoints(humanoid)):
      p.changeDynamics(humanoid, j, linearDamping=0, angularDamping=0)
      info = p.getJointInfo(humanoid, j)
      # print j,info[1]
      jointName = info[1]
      jointType = info[2]
      if (jointType == p.JOINT_PRISMATIC or jointType == p.JOINT_REVOLUTE):
        jointIds.append(j)
        # paramIds.append(p.addUserDebugParameter(jointName.decode("utf-8"), -4, 4, 0))
    # print "JJ",len(jointIds)
    return jointIds,humanoid


class OrganUpdater:
    def __init__(self,i,c,jIDs,hum):
        self.c = c
        self.i = i
        self.hum = hum
        self.targetPos = c#p.readUserDebugParameter(self.c)
        self.movements = []
        self.jointIds = jIDs

    def addMovement(self,mov):
        mov["time"] = mov["off"]
        self.movements.append(mov)

    def update(self,inc):
        self.targetPos += inc
        if self.targetPos >= 0.5:
            self.targetPos = 0.5
        if self.targetPos <= -0.5:
            self.targetPos = -0.5
        p.setJointMotorControl2(self.hum,
            self.jointIds[self.i],
            p.POSITION_CONTROL,
            self.targetPos,
            force=5 * 240.)

    def stepUpdate(self,e):
        for mov in self.movements:
            if mov["time"] <= 0:
                self.update(mov["strength"])
                mov["time"] = mov["rep"]
            else:
                mov["time"] -= 1



class HumanUpdater:
    def __init__(self,jIDs,hum,movements):
        self.jointIds = jIDs
        self.hum = hum
        self.organs = [OrganUpdater(i,self.jointIds[i],jIDs,hum) for i in range(len(self.jointIds))]
        for mov in movements:
            # print len(self.organs),mov["id"]
            self.organs[int(mov["id"])].addMovement(mov)


    def getDist(self):
        pos,rot = p.getBasePositionAndOrientation(self.hum)
        # print pos[2]
        if pos[2]<0.6:
            return -1,True
        return round(pos[0],2),False

    def updateOrgan(self,oid,inc):
        self.organs[oid].update(inc)

    def stepUpdate(self,e):
        for o in self.organs:
            o.stepUpdate(e)


def simulateAndEval(movements,show=False):
    jIDs,hum = init_bullet(show)
    myhuman = HumanUpdater(jIDs,hum,movements)
    p.setRealTimeSimulation(0)
    p.setGravity(0, 0, -10)
    maxdist = 0
    for epoch in range(1000):
        myhuman.stepUpdate(epoch)
        dist,fall = myhuman.getDist()
        if dist>maxdist:
            maxdist = dist
        if fall:
            p.disconnect()
            return maxdist
        # print "[",epoch,"] Dist:",dist
        p.stepSimulation()
        if show:
            time.sleep(0.01)
    p.disconnect()
    return maxdist

def parseMovements(mov):
    movements = []
    for m in mov:
        movements.append({
            "id":math.floor(m[0]),
            "strength":m[1],
            "rep":m[2],
            "off":m[3]
        })
    return movements
