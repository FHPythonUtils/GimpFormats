from __future__ import annotations

from aenum import Enum, extend_enum


# pyright: reportGeneralTypeIssues=false
class ColorMode(Enum):
	RGB = "RGB"
	Grayscale = "Grayscale"
	Indexed = "Indexed"


class Units(Enum):
	Inches = "Inches"
	Millimetres = "Millimetres"
	Points = "Points"
	Picas = "Picas"


class CompositeMode(Enum):
	Union = "Union"
	Clip_to_backdrop = "Clip to backdrop"
	Clip_to_layer = "Clip to layer"
	Intersection = "Intersection"


class CompositeSpace(Enum):
	RGB_linear = "RGB (linear)"
	RGB_profile = "RGB (from color profile)"
	LAB = "LAB"
	RGB_perceptual = "RGB (perceptual)"


class TagColor(Enum):
	None_Color = "None"
	Blue = "Blue"
	Green = "Green"
	Yellow = "Yellow"
	Orange = "Orange"
	Brown = "Brown"
	Red = "Red"
	Violet = "Violet"
	Gray = "Gray"


class CompressionMode(Enum):
	None_Compression = "None"
	RLE = "RLE"
	Zlib = "Zlib"
	Fractal = "Fractal"


class GimpBlendMode(Enum):
	# Since 'ancient times' 0-9
	NORMAL_LEGACY = "Normal (legacy)"
	DISSOLVE_LEGACY = "Dissolve (legacy)"
	BEHIND_LEGACY = "Behind (legacy)"
	MULTIPLY_LEGACY = "Multiply (legacy)"
	SCREEN_LEGACY = "Screen (legacy)"
	OLD_BROKEN_OVERLAY = "Old broken Overlay"
	DIFFERENCE_LEGACY = "Difference (legacy)"
	ADDITION_LEGACY = "Addition (legacy)"
	SUBTRACT_LEGACY = "Subtract (legacy)"
	DARKEN_ONLY_LEGACY = "Darken only (legacy)"

	# Since 'ancient times' 10-18
	LIGHTEN_ONLY_LEGACY = "Lighten only (legacy)"
	HUE_HSV_LEGACY = "Hue (HSV) (legacy)"
	SATURATION_HSV_LEGACY = "Saturation (HSV) (legacy)"
	COLOR_HSL_LEGACY = "Color (HSL) (legacy)"
	VALUE_HSV_LEGACY = "Value (HSV) (legacy)"
	DIVIDE_LEGACY = "Divide (legacy)"
	DODGE_LEGACY = "Dodge (legacy)"
	BURN_LEGACY = "Burn (legacy)"
	HARD_LIGHT_LEGACY = "Hard Light (legacy)"
	# Since XCF 2 19
	SOFT_LIGHT_LEGACY = "Soft light (legacy)"

	# Since XCF 2 20-22
	GRAIN_EXTRACT_LEGACY = "Grain extract (legacy)"
	GRAIN_MERGE_LEGACY = "Grain merge (legacy)"
	COLOR_ERASE_LEGACY = "Color erase (legacy)"

	# Since XCF 9 23-27
	OVERLAY = "Overlay"
	HUE_LCH = "Hue (LCH)"
	CHROMA_LCH = "Chroma (LCH)"
	COLOR_LCH = "Color (LCH)"
	LIGHTNESS_LCH = "Lightness (LCH)"

	# Since XCF 10 28-29
	NORMAL = "Normal"
	BEHIND = "Behind"

	# Since XCF 10 30-39
	MULTIPLY = "Multiply"
	SCREEN = "Screen"
	DIFFERENCE = "Difference"
	ADDITION = "Addition"
	SUBSTRACT = "Substract"
	DARKEN_ONLY = "Darken only"
	LIGHTEN_ONLY = "Lighten only"
	HUE_HSV = "Hue (HSV)"
	SATURATION_HSV = "Saturation (HSV)"
	COLOR_HSL = "Color (HSL)"

	# Since XCF 10 40-49
	VALUE_HSV = "Value (HSV)"
	DIVIDE = "Divide"
	DODGE = "Dodge"
	BURN = "Burn"
	HARD_LIGHT = "Hard light"
	SOFT_LIGHT = "Soft light"
	GRAIN_EXTRACT = "Grain extract"
	GRAIN_MERGE = "Grain merge"
	VIVID_LIGHT = "Vivid light"
	PIN_LIGHT = "Pin light"

	# Since XCF 10 50-59
	LINEAR_LIGHT = "Linear light"
	HARD_MIX = "Hard mix"
	EXCLUSION = "Exclusion"
	LINEAR_BURN = "Linear burn"
	LUMA_DARKEN_ONLY = "Luma/Luminance darken only"
	LUMA_LIGHTEN_ONLY = "Luma/Luminance lighten only"
	LUMINANCE = "Luminance"
	COLOR_ERASE = "Color erase"
	ERASE = "Erase"
	MERGE = "Merge"

	# Since XCF 10 60-61
	SPLIT = "Split"
	PASS_THROUGH = "Pass through"  # noqa: S105


def merge_to(src: Enum, dest: Enum):
	for name, value in src.__members__.items():
		if name not in dest.__dict__:
			extend_enum(dest, name, value.value)


class GeneralProperties(Enum):
	PROP_END = 0
	PROP_FLOAT_OPACITY = 33
	PROP_COLOR_TAG = 34
	PROP_LINKED = 9
	PROP_LOCK_CONTENT = 28
	PROP_LOCK_POSITION = 32
	PROP_OPACITY = 6
	PROP_PARASITES = 21
	PROP_VISIBLE = 8
	PROP_TATTOO = 20
	# PROP_ITEM_SET_ITEM = 41
	PROP_LOCK_VISIBILITY = 42


class ImageProperties(Enum):
	PROP_PARASITES = 21
	PROP_TATTOO = 20
	PROP_END = 0
	PROP_COLORMAP = 1
	PROP_COMPRESSION = 17
	PROP_GUIDES = 18
	PROP_RESOLUTION = 19
	PROP_PATHS = 23
	PROP_SAMPLE_POINTS = 39
	PROP_UNIT = 22
	PROP_USER_UNIT = 24
	PROP_VECTORS = 25
	PROP_OLD_SAMPLE_POINTS = 27

	# PROP_ITEM_SET  = 40


class ChannelProperties(Enum):
	PROP_ACTIVE_CHANNEL = 3
	PROP_COLOR = 16
	PROP_FLOAT_COLOR = 38
	PROP_SELECTION = 4
	PROP_SHOW_MASKED = 14


merge_to(src=GeneralProperties, dest=ChannelProperties)


class LayerProperties(Enum):
	PROP_ACTIVE_LAYER = 2
	PROP_APPLY_MASK = 11
	PROP_COMPOSITE_MODE = 35
	PROP_COMPOSITE_SPACE = 36
	PROP_BLEND_SPACE = 37
	PROP_EDIT_MASK = 12
	PROP_FLOATING_SELECTION = 5
	PROP_GROUP_ITEM = 29
	PROP_ITEM_PATH = 30
	PROP_GROUP_ITEM_FLAGS = 31
	PROP_MODE = 7
	PROP_LOCK_ALPHA = 10
	PROP_SHOW_MASK = 13
	PROP_OFFSETS = 15
	PROP_TEXT_LAYER_FLAGS = 26


merge_to(src=GeneralProperties, dest=LayerProperties)


class AllProps(Enum):
	pass


merge_to(src=LayerProperties, dest=AllProps)
merge_to(src=ChannelProperties, dest=AllProps)
merge_to(src=ImageProperties, dest=AllProps)
