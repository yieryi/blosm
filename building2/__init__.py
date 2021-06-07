from mathutils import Vector
import parse
from util.polygon import Polygon


class Building:
    """
    A class representing the building for the renderer
    """
    
    actions = []
    
    def __init__(self):
        self.verts = []
        # counterparts for <self.verts> in the BMesh
        self.bmVerts = []
        # A cache to store different stuff:
        # attributes evaluated per building rather than per footprint, cladding texture info
        self._cache = {}
        # <self.outlinePolygon> is used only in the case if the buildings has parts
        self.outlinePolygon = Polygon()
    
    def init(self):
        self.verts.clear()
        self.bmVerts.clear()
        self.offset = None
        # Instance of item.footprint.Footprint, it's only used if the building definition
        # in the data model doesn't contain building parts, i.e. the building is defined completely
        # by its outline
        self.footprint = None
        self._cache.clear()
        self.assetInfoBldgIndex = None
        self._area = 0.
        # altitude difference for the building footprint projected on the terrain
        self.altitudeDifference = 0.
        
        # attributes from @meta of the style block
        self.buildingUse = None
        self.classifyFacades = 1
    
    def clone(self):
        building = Building()
        return building
    
    @classmethod
    def getItem(cls, itemFactory, data):
        item = itemFactory.getItem(cls)
        item.init()
        item.data = data
        return item
    
    def setStyleMeta(self, style):
        if style.meta:
            for attr in style.meta.attrs:
                setattr(self, attr, style.meta.attrs[attr])