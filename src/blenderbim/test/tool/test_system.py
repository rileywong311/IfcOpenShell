# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
from test.bim.bootstrap import NewFile
from blenderbim.tool.system import System as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.System)


class TestDisableEditingSystem(NewFile):
    def test_run(self):
        bpy.context.scene.BIMSystemProperties.active_system_id = 10
        subject.disable_editing_system()
        assert bpy.context.scene.BIMSystemProperties.active_system_id == 0


class TestDisableSystemEditingUI(NewFile):
    def test_run(self):
        subject.enable_system_editing_ui()
        subject.disable_system_editing_ui()
        assert bpy.context.scene.BIMSystemProperties.is_editing is False


class TestEnableSystemEditingUI(NewFile):
    def test_run(self):
        subject.enable_system_editing_ui()
        assert bpy.context.scene.BIMSystemProperties.is_editing is True


class TestExportSystemAttributes(NewFile):
    def test_run(self):
        TestImportSystemAttributes().test_importing_a_system()
        assert subject.export_system_attributes() == {
            "GlobalId": "GlobalId",
            "Name": "Name",
            "Description": "Description",
            "ObjectType": "ObjectType",
        }


class TestImportSystemAttributes(NewFile):
    def test_importing_a_system(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcSystem()
        system.GlobalId = "GlobalId"
        system.Name = "Name"
        system.Description = "Description"
        system.ObjectType = "ObjectType"
        subject().import_system_attributes(system)
        props = bpy.context.scene.BIMSystemProperties
        assert props.system_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.system_attributes.get("Name").string_value == "Name"
        assert props.system_attributes.get("Description").string_value == "Description"
        assert props.system_attributes.get("ObjectType").string_value == "ObjectType"

    def test_importing_a_building_system(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcBuildingSystem()
        system.GlobalId = "GlobalId"
        system.Name = "Name"
        system.Description = "Description"
        system.ObjectType = "ObjectType"
        system.PredefinedType = "SHADING"
        system.LongName = "LongName"
        subject().import_system_attributes(system)
        props = bpy.context.scene.BIMSystemProperties
        assert props.system_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.system_attributes.get("Name").string_value == "Name"
        assert props.system_attributes.get("Description").string_value == "Description"
        assert props.system_attributes.get("ObjectType").string_value == "ObjectType"
        assert props.system_attributes.get("PredefinedType").enum_value == "SHADING"
        assert props.system_attributes.get("LongName").string_value == "LongName"

    def test_importing_a_distribution_system(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcDistributionSystem()
        system.GlobalId = "GlobalId"
        system.Name = "Name"
        system.Description = "Description"
        system.ObjectType = "ObjectType"
        system.PredefinedType = "ELECTRICAL"
        system.LongName = "LongName"
        subject().import_system_attributes(system)
        props = bpy.context.scene.BIMSystemProperties
        assert props.system_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.system_attributes.get("Name").string_value == "Name"
        assert props.system_attributes.get("Description").string_value == "Description"
        assert props.system_attributes.get("ObjectType").string_value == "ObjectType"
        assert props.system_attributes.get("PredefinedType").enum_value == "ELECTRICAL"
        assert props.system_attributes.get("LongName").string_value == "LongName"


class TestImportSystems(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifc.createIfcDistributionSystem()
        zone = ifc.createIfcZone()
        subject.import_systems()
        props = bpy.context.scene.BIMSystemProperties
        assert len(props.systems) == 1
        assert props.systems[0].ifc_definition_id == system.id()
        assert props.systems[0].name == "Unnamed"
        assert props.systems[0].ifc_class == "IfcDistributionSystem"


class TestSelectSystemProducts(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        element = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcPump")
        system = ifcopenshell.api.run("system.add_system", ifc, ifc_class="IfcSystem")
        ifcopenshell.api.run("system.assign_system", ifc, product=element, system=system)
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(element, obj)
        subject.select_system_products(system)
        assert obj in bpy.context.selected_objects


class TestSetActiveSystem(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        system = ifcopenshell.api.run("system.add_system", ifc, ifc_class="IfcSystem")
        subject.set_active_system(system)
        assert bpy.context.scene.BIMSystemProperties.active_system_id == system.id()