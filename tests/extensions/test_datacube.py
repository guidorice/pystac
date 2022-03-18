import unittest
import pystac
from pystac import ExtensionTypeError
from pystac.extensions.datacube import (
    AdditionalDimension,
    DatacubeExtension,
    Dimension,
    DimensionType,
    HorizontalSpatialDimension,
    HorizontalSpatialDimensionAxis,
    TemporalDimension,
    Variable,
    VerticalSpatialDimension,
    VerticalSpatialDimensionAxis,
)

from tests.utils import TestCases


class DatacubeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.example_uri = TestCases.get_path("data-files/datacube/item.json")

    def test_validate_datacube(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        item.validate()

    def test_extension_not_implemented(self) -> None:
        # Should raise exception if Item does not include extension URI
        item = pystac.Item.from_file(self.example_uri)
        item.stac_extensions.remove(DatacubeExtension.get_schema_uri())

        with self.assertRaises(pystac.ExtensionNotImplemented):
            _ = DatacubeExtension.ext(item)

        # Should raise exception if owning Item does not include extension URI
        asset = item.assets["data"]

        with self.assertRaises(pystac.ExtensionNotImplemented):
            _ = DatacubeExtension.ext(asset)

        # Should succeed if Asset has no owner
        ownerless_asset = pystac.Asset.from_dict(asset.to_dict())
        _ = DatacubeExtension.ext(ownerless_asset)

    def test_item_ext_add_to(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        item.stac_extensions.remove(DatacubeExtension.get_schema_uri())
        self.assertNotIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)

        _ = DatacubeExtension.ext(item, add_if_missing=True)

        self.assertIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)

    def test_asset_ext_add_to(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        item.stac_extensions.remove(DatacubeExtension.get_schema_uri())
        self.assertNotIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)
        asset = item.assets["data"]

        _ = DatacubeExtension.ext(asset, add_if_missing=True)

        self.assertIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)

    def test_should_raise_exception_when_passing_invalid_extension_object(
        self,
    ) -> None:
        self.assertRaisesRegex(
            ExtensionTypeError,
            r"^Datacube extension does not apply to type 'object'$",
            DatacubeExtension.ext,
            object(),
        )

    def test_get_variables(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        dc_ext = DatacubeExtension.ext(item)

        assert dc_ext.variables is not None
        self.assertIsInstance(dc_ext.variables, dict)
        self.assertNotEqual(dc_ext.variables, {})

        for var in dc_ext.variables.values():
            self.assertIsInstance(var, Variable)

    def test_set_variables(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        dc_ext = DatacubeExtension.ext(item)

        new_variable = Variable.from_dict(
            {"dimensions": ["time", "y", "x", "pressure_levels"], "type": "data"}
        )
        new_variables = {"temp": new_variable}

        dc_ext.variables = new_variables

        self.assertEqual(
            item.properties["cube:variables"], {"temp": new_variable.to_dict()}
        )


class HorizontalSpatialDimensionTest(unittest.TestCase):
    def test_from_dict(self) -> None:
        desc = "explains the dimension"
        dim = Dimension.from_dict(
            dict(
                type=DimensionType.SPATIAL,
                axis=HorizontalSpatialDimensionAxis.X,
                description=desc,
            )
        )
        self.assertIsInstance(dim, HorizontalSpatialDimension)
        self.assertEqual(dim.description, desc)
        self.assertEqual(dim.dim_type, DimensionType.SPATIAL)
        self.assertEqual(dim.axis, HorizontalSpatialDimensionAxis.X)  # type: ignore

        dim = Dimension.from_dict(
            dict(
                type=DimensionType.SPATIAL,
                axis=HorizontalSpatialDimensionAxis.Y,
                description=desc,
            )
        )
        self.assertIsInstance(dim, HorizontalSpatialDimension)
        self.assertEqual(dim.description, desc)
        self.assertEqual(dim.dim_type, DimensionType.SPATIAL)
        self.assertEqual(dim.axis, HorizontalSpatialDimensionAxis.Y)  # type: ignore


class VerticalSpatialDimensionTest(unittest.TestCase):
    def test_from_dict(self) -> None:
        desc = "explains the dimension"
        dim = Dimension.from_dict(
            dict(
                type=DimensionType.SPATIAL,
                axis=VerticalSpatialDimensionAxis.Z,
                description=desc,
            )
        )
        self.assertIsInstance(dim, VerticalSpatialDimension)
        self.assertEqual(dim.description, desc)
        self.assertEqual(dim.dim_type, DimensionType.SPATIAL)
        self.assertEqual(dim.axis, VerticalSpatialDimensionAxis.Z)  # type: ignore


class TemporalDimensionTest(unittest.TestCase):
    def test_from_dict(self) -> None:
        desc = "explains the dimension"
        dim = Dimension.from_dict(dict(type=DimensionType.TEMPORAL, description=desc))
        self.assertIsInstance(dim, TemporalDimension)
        self.assertEqual(dim.description, desc)
        self.assertEqual(dim.dim_type, DimensionType.TEMPORAL)


class AdditionalDimensionTest(unittest.TestCase):
    def test_from_dict(self) -> None:
        desc = "explains the dimension"
        dim = Dimension.from_dict(dict(type="other", description=desc))
        self.assertIsInstance(dim, AdditionalDimension)
        self.assertEqual(dim.description, desc)
