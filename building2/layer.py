from operator import attrgetter

from building.layer import BuildingLayer

from renderer import Renderer
from util.blender import getBmesh, setBmesh, addGeometryNodesModifier, useAttributeForGnInput


class RealisticBuildingLayer(BuildingLayer):
    
    def __init__(self, layerId, app):
        super().__init__(layerId, app)
        
        self.gnMeshAttributes = (
            "asset_index",
            "vector",
            "scale"#,
            #"extra"
        )
        
        # the name for the base UV map used for facade textures
        self.uvLayerNameFacade = "facade"
        
        # A Blender object for vertex clouds. 3D-modules representing a basic building appearance
        # will be instanced on those vertices.
        self.objGn = None
        # <self.objGnExtra> will be used for the future development
        # Additional details may be added (like, air vents, flowers, interiors).
        # Those 3D-modules for the details will be instanced on vertices that belong to
        # the Blender object(s) <self.objGnExtra>.
        # <self.objGnExtra> could be a single Blender object or a list of Blender objects
        self.objGnExtra = None

    def prepare(self):
        # below is the TEMPORARY oode to place roof objects on float roofs
        
        if self.app.preferMesh:
            # create attributes for the Geometry Nodes
            objGnMesh = self.obj.data
            # an asset index in Blender collection <globalRenderer.buildingAssetsCollection>
            objGnMesh.attributes.new("triangulate", 'BOOLEAN', 'FACE')
            objGnMesh.attributes.new("subdivide_level", 'INT', 'FACE')
        
        super().prepare()
    
    def finalize(self, globalRenderer):
        super().finalize()
        
        if self.app.preferMesh:
            gnMeshAttributes = self.gnMeshAttributes
            objGn = self.objGn
            
            setBmesh(objGn, self.bmGn)
            
            # create attributes for the Geometry Nodes
            objGnMesh = self.objGn.data
            # an asset index in Blender collection <globalRenderer.buildingAssetsCollection>
            assetIndex = objGnMesh.attributes.new(gnMeshAttributes[0], 'INT', 'POINT').data
            # a unit vector along the related building facade
            unitVector = objGnMesh.attributes.new(gnMeshAttributes[1], 'FLOAT_VECTOR', 'POINT').data
            # 3 float numbers to scale an instance along its local x, y and z axes
            scale = objGnMesh.attributes.new(gnMeshAttributes[2], 'FLOAT_VECTOR', 'POINT').data
            # 2 float additional numbers. They are used only by corner modules for now
            #extra = objGnMesh.attributes.new(gnMeshAttributes[3], 'FLOAT_VECTOR', 'POINT').data
            
            # Indices in <assetIndex> refer to Blender objects in Blender collection
            # <globalRenderer.buildingAssetsCollection> sorted by the name of the Blender object.
            # That's way we need the Python dictionary <objNameToIndex> for mapping between
            # the name of the Blender object and its index after the sorting
            objNameToIndex = dict(
                (objName.name,index) for index,objName in enumerate(
                    sorted(globalRenderer.buildingAssetsCollection.objects, key=attrgetter("name"))
                )
            )
            
            #for index, (objName, _unitVector, scaleX, scaleZ, extra) in enumerate(self.attributeValuesGn):
            for index, (objName, _unitVector, scaleX, scaleZ) in enumerate(self.attributeValuesGn):
                assetIndex[index].value = objNameToIndex[objName]
                unitVector[index].vector = _unitVector
                scale[index].vector = (scaleX, 1., scaleZ)
                #if extra:
                #    extra[index].vector = extra
            
            self.attributeValuesGn.clear()
            
            # create a modifier for the Geometry Nodes setup
            m = addGeometryNodesModifier(objGn, globalRenderer.gnBuilding, "Buildings")
            # <mAttrs> have the form like: 
            # [
            #     "Input_4", "Input_4_use_attribute", "Input_4_attribute_name",
            #     "Input_3", "Input_3_use_attribute", "Input_3_attribute_name"
            # ]
            mAttrs = list(m.keys())
            for i1,i2 in zip( range(0, len(mAttrs), 3), range(len(mAttrs)//3) ):
                useAttributeForGnInput(m, mAttrs[i1], gnMeshAttributes[i2])
            
            # TEMPORARY code below to place objects on flat roofs
            # set attributes
            for index, (triangulate, subdivide_level) in enumerate(self.attributeValuesFlatRoof):
                self.obj.data.attributes["triangulate"].data[index].value = triangulate
                self.obj.data.attributes["subdivide_level"].data[index].value = subdivide_level
            self.attributeValuesFlatRoof.clear()
            # create a modifier for the Geometry Nodes setup
            m = addGeometryNodesModifier(self.obj, globalRenderer.gnFlatRoof, "Objects on flat roofs")
            # triangulate
            useAttributeForGnInput(m, "Input_10", "triangulate")
            # The parameter <free_area_factor>: the probability that an area will be deleted in
            # the Geometry-Nodes-setup and therefore will not host a flat roof object
            m["Input_11"] = 0.2
            # subdivide_level
            useAttributeForGnInput(m, "Input_12", "subdivide_level")


class RealisticBuildingLayerBase(RealisticBuildingLayer):
        
    def __init__(self, layerId, app):
        super().__init__(layerId, app)
        
        # the name for the auxiliary UV map used for claddding textures
        self.uvLayerNameCladding = "cladding"
        # the name for the vertex color layer
        self.vertexColorLayerNameCladding = "cladding_color"
    
    def prepare(self):
        mesh = self.obj.data
        uv_layers = mesh.uv_layers
        uv_layers.new(name=self.uvLayerNameFacade)
        uv_layers.new(name=self.uvLayerNameCladding)
        
        mesh.vertex_colors.new(name=self.vertexColorLayerNameCladding)
        
        super().prepare()
        
        if self.app.preferMesh:
            obj = self.obj
            # copy the values from <self.obj>
            self.objGn = Renderer.createBlenderObject(
                obj.name + "_gn",
                obj.location,
                obj.users_collection[0],
                obj.parent
            )
            
            self.attributeValuesGn = []
            
            self.attributeValuesFlatRoof = []
            
            self.bmGn = getBmesh(self.objGn)


class RealisticBuildingLayerExport(RealisticBuildingLayer):
        
    def __init__(self, layerId, app):
        super().__init__(layerId, app)
        
        # The name for the base UV map used for cladding textures.
        # The same UV-map is used for both the facade and cladding textures
        self.uvLayerNameCladding = "facade"
    
    def prepare(self, instance):
        mesh = instance.obj.data
        uv_layers = mesh.uv_layers
        uv_layers.new(name=self.uvLayerNameFacade)
        
        super().prepare(instance)