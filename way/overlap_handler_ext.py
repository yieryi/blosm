from lib.CompGeom.centerline import pointInPolygon

# helper functions -----------------------------------------------
def cyclePair(iterable):
    # iterable -> (p0,p1), (p1,p2), (p2, p3), ..., (pn, p0)
    prevs, nexts = tee(iterable)
    prevs = islice(cycle(prevs), len(iterable) - 1, None)
    return zip(prevs,nexts)

def pairs(iterable):
    # iterable -> (p0,p1), (p1,p2), (p2, p3), ...
    p1, p2 = tee(iterable)
    next(p2, None)
    return zip(p1,p2)

# Adapted from https://stackoverflow.com/questions/16542042/fastest-way-to-sort-vectors-by-angle-without-actually-computing-that-angle
# Input:  d: vector.
# Output: a number from the range [0 .. 4] which is monotonic
#         in the angle this vector makes against the x axis.
def pseudoangle(d):
    p = d[0]/(abs(d[0])+abs(d[1])) # -1 .. 1 increasing with x
    return 3 + p if d[1] < 0 else 1 - p 
# ----------------------------------------------------------------

from debugPlot import *

def areaFromEndClusters(cls,ovH):
    # ovH is the overlapHandler

    nodeOutWays = []
    n = len(ovH.outIsects)-1
    for indx,(isect,inID) in enumerate(zip(ovH.outIsects,ovH.wIDs)):
        wayPos = 'right' if indx==0 else 'left' if indx==n else 'mid'
        nodeOutWays.append( NodeOutWays(cls,ovH,isect,inID,wayPos) )
    plotEnd()
    pass


class NodeOutWays():
    ID = 0
    def __init__(self,cls,ovH,isect,inID,wayPos):
        self.id = NodeOutWays.ID
        NodeOutWays.ID += 1
        self.cls = cls
        self.wayPos = wayPos
        self.ovH = ovH

        # Get the IDs of all way-sections that leave this node.
        node = isect.freeze()
        outIds = self.getOutSectionIds(node,inID)

        # If it was an end-node, there are no out-ways. Invalidate this instance.
        if not outIds:
            self.valid = False
            return

        # A filtering is required to removw ways that pint into the cluster, wherever
        # they came from. First we need to construct vectors that point to the right
        # an to the left, perpendicularly to the way in the cluster.
        outVInID = self.outVector(node,inID) # Vector of the way into hte cluster.
        perpVL = Vector((outVInID[1],-outVInID[0]))/outVInID.length
        perpVR = Vector((-outVInID[1],outVInID[0]))/outVInID.length

        # These vectors are inserted as first elements into a list of vectors of all
        # ways leaving this node. The indices i in <allVectors> are as follows:
        # 0: cluster-way
        # 1: perp to the left
        # 2: perp to the right
        # 3: first vector in outIds: Id = i-3
        # :
        outVectors = [self.outVector(node, Id) for Id in outIds]
        allVectors = [self.outVector(node, inID),perpVL,perpVR] + outVectors

        # An argsort of the angles delivers a circular list of the above indices,
        # where the angles of the vectors around the node are eorted counter-clockwise,
        # and where the special vectors with indices 0 .. 2 are easily to find.
        sortedIDs = sorted( range(len(allVectors)), key=lambda indx: pseudoangle(allVectors[indx]))

        # plt.subplot(1,2,1)
        # for i,outway in enumerate(outVectors):
        #     plotLine([Vector((0,0)),outway])
        #     plotText(outway,' '+str(i))
        # plotLine([Vector((0,0)),self.outVector(node, inID)],'r')      
        # plt.gca().axis('equal')

        # Depending on the position of the node at the cluster end, only ways within an angle range
        # are allowed. 
        if wayPos == 'right':
            # All ways between the cluster-way and the left perp are valid.
            start = sortedIDs.index(0)  # index of cluster-way
            shifted = sortedIDs[start:] + sortedIDs[:start]  # shift this index as first element
            end = shifted.index(1)  # Index of left perp
            filteredIDs = [Id for Id in shifted[0:end] if Id not in [0,1,2]]
        elif wayPos == 'left':
            # All ways between the right perp and the cluster-way are valid.
            start = sortedIDs.index(2)  # index of right perp
            shifted = sortedIDs[start:] + sortedIDs[:start]  # shift this index as first element
            end = shifted.index(0)  # Index of lcluster-way
            filteredIDs = [Id for Id in shifted[0:end] if Id not in [0,1,2]]
        elif wayPos == 'mid': 
            # All ways between the right perp and left perp are valid.
            start = sortedIDs.index(2)  # index of right perp
            shifted = sortedIDs[start:] + sortedIDs[:start]  # shift this index as first element
            end = shifted.index(1)  # Index of left perp
            filteredIDs = [Id for Id in shifted[0:end] if Id not in [0,1,2]]

        # plt.subplot(1,2,2)
        for Id in filteredIDs:
            outway = outVectors[Id-3]
            plotLine([Vector((0,0)),outway])
            plotText(outway,' '+str(Id-3))
        plotLine([Vector((0,0)),self.outVector(node, inID)],'r')    
        plt.title(wayPos)  
        # plotEnd()

        # # Create polygon of cluster border
        # poly = self.ovH.subCluster.centerline.buffer(self.ovH.subCluster.outWL(),self.ovH.subCluster.outWR())

        # for i,outway in enumerate(outWays):
        #     plotLine([Vector((0,0)),outway])
        #     plotText(outway,' '+str(i))
        # plotLine([Vector((0,0)),outVInID],'r',4)
        # plotLine([Vector((0,0)),perpVL],'green',4)
        # plotLine([Vector((0,0)),perpVR],'orange',4)
        # plt.title(wayPos)
        # plotEnd()

        # outWayIDs = sorted( range(len(allVectors)), key=lambda indx: pseudoangle(allVectors[indx]))
        test = 1

        # if wayPos == 'right':
        #     # All ways between the way-cluster and the left perp are valid.
        #     # Make the in-way as the first way.
        #     self.outWays = self.outWays[clusterIndx:] + self.outWays[:clusterIndx]




        # perpVLIndx = outWays.index(perpVL)
        # perpVRIndx = outWays.index(perpVR)
        # inIndx = outWays.index(outVInID)
        # test=1


        # poly = self.ovH.subCluster.centerline.buffer(self.ovH.subCluster.outWL(),self.ovH.subCluster.outWR())
        # plotPolygon(poly,False,'g','g',1,True)
        # cls.waySections[inID].polyline.plot('r',3,True)
        # for Id in outIds:
        #     cls.waySections[Id].polyline.plot('k')
        # plotEnd()



    def outVector(self,node, wayID):
        s = self.cls.waySections
        outV = s[wayID].polyline[1]-s[wayID].polyline[0] if s[wayID].polyline[0] == node else s[wayID].polyline[-2]-s[wayID].polyline[-1]
        outV /= outV.length
        return outV



    # Find the IDs of all way-sections that leave the <node>, but are not inside the way-cluster.
    def getOutSectionIds(self,node,inID):
        outSectionIDs = []
        if node in self.cls.sectionNetwork:
            for net_section in self.cls.sectionNetwork.iterOutSegments(node):
                if net_section.category != 'scene_border':
                    if net_section.sectionId != inID:
                        # If one of the nodes is outside of the clusters ...
                        if not (net_section.s in self.ovH.outIsects and net_section.t in self.ovH.outIsects):                               
                            outSectionIDs.append(net_section.sectionId)
                        else: # ... else we have to check if this section is inside or outside of the way-cluster.
                            nonNodeVerts = net_section.path[1:-1]
                            if len(nonNodeVerts): # There are vertices beside the nodes at the ends.
                                # Check, if any of these vertices is outside of the way-cluster
                                clusterPoly = self.ovH.subCluster.centerline.buffer(self.ovH.subCluster.endWidth/2.,self.ovH.subCluster.endWidth/2.)
                                if any( pointInPolygon(clusterPoly,vert) == 'OUT' for vert in nonNodeVerts ):
                                    outSectionIDs.append(net_section.sectionId) # There are, so keep this way ...
                                    continue
                                # ... else invalidate this way
                                self.cls.waySections[net_section.sectionId].isValid = False
        return outSectionIDs    

