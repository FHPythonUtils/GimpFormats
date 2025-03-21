# Gimpiobase

[Gimpformats Index](../README.md#gimpformats-index) / [Gimpformats](./index.md#gimpformats) / Gimpiobase

> Auto-generated documentation for [gimpformats.GimpIOBase](../../../gimpformats/GimpIOBase.py) module.

- [Gimpiobase](#gimpiobase)
  - [GimpIOBase](#gimpiobase)
    - [GimpIOBase().__repr__](#gimpiobase()__repr__)
    - [GimpIOBase().__str__](#gimpiobase()__str__)
    - [GimpIOBase()._colormapDecode](#gimpiobase()_colormapdecode)
    - [GimpIOBase()._guidelinesDecode](#gimpiobase()_guidelinesdecode)
    - [GimpIOBase()._itemPathDecode](#gimpiobase()_itempathdecode)
    - [GimpIOBase()._parasitesDecode](#gimpiobase()_parasitesdecode)
    - [GimpIOBase()._parasitesEncode](#gimpiobase()_parasitesencode)
    - [GimpIOBase()._propertiesDecode](#gimpiobase()_propertiesdecode)
    - [GimpIOBase()._propertiesEncode](#gimpiobase()_propertiesencode)
    - [GimpIOBase()._propertyDecode](#gimpiobase()_propertydecode)
    - [GimpIOBase()._propertyEncode](#gimpiobase()_propertyencode)
    - [GimpIOBase()._samplePointsDecode](#gimpiobase()_samplepointsdecode)
    - [GimpIOBase()._userUnitsDecode](#gimpiobase()_userunitsdecode)
    - [GimpIOBase()._vectorsDecode](#gimpiobase()_vectorsdecode)
    - [GimpIOBase().activeVector](#gimpiobase()activevector)
    - [GimpIOBase().doc](#gimpiobase()doc)
    - [GimpIOBase().expanded](#gimpiobase()expanded)
    - [GimpIOBase().expanded](#gimpiobase()expanded-1)
    - [GimpIOBase().full_repr](#gimpiobase()full_repr)
    - [GimpIOBase().pointerSize](#gimpiobase()pointersize)
    - [GimpIOBase().root](#gimpiobase()root)
    - [GimpIOBase().tattoo](#gimpiobase()tattoo)
    - [GimpIOBase().tattoo](#gimpiobase()tattoo-1)
  - [GimpUserUnits](#gimpuserunits)
    - [GimpUserUnits().__str__](#gimpuserunits()__str__)
    - [GimpUserUnits().decode](#gimpuserunits()decode)
    - [GimpUserUnits().encode](#gimpuserunits()encode)
    - [GimpUserUnits().full_repr](#gimpuserunits()full_repr)
  - [camel_to_pascal_with_spaces](#camel_to_pascal_with_spaces)

## GimpIOBase

[Show source in GimpIOBase.py:37](../../../gimpformats/GimpIOBase.py#L37)

#### Signature

```python
class GimpIOBase:
    def __init__(self, parent: Any = None) -> None: ...
```

### GimpIOBase().__repr__

[Show source in GimpIOBase.py:555](../../../gimpformats/GimpIOBase.py#L555)

Get a textual representation of this object.

#### Signature

```python
def __repr__(self) -> str: ...
```

### GimpIOBase().__str__

[Show source in GimpIOBase.py:551](../../../gimpformats/GimpIOBase.py#L551)

Get a textual representation of this object.

#### Signature

```python
def __str__(self) -> str: ...
```

### GimpIOBase()._colormapDecode

[Show source in GimpIOBase.py:197](../../../gimpformats/GimpIOBase.py#L197)

_colormapDecode_.

#### Arguments

- `data` - can be bytearray or an IO object

decode colormap/palette

#### Signature

```python
def _colormapDecode(self, data: bytearray | IO, index: int = 0) -> None: ...
```

### GimpIOBase()._guidelinesDecode

[Show source in GimpIOBase.py:145](../../../gimpformats/GimpIOBase.py#L145)

Decode guidelines.

#### Signature

```python
def _guidelinesDecode(self, data: bytearray) -> None: ...
```

### GimpIOBase()._itemPathDecode

[Show source in GimpIOBase.py:155](../../../gimpformats/GimpIOBase.py#L155)

Decode item path.

#### Signature

```python
def _itemPathDecode(self, data: bytearray) -> None: ...
```

### GimpIOBase()._parasitesDecode

[Show source in GimpIOBase.py:128](../../../gimpformats/GimpIOBase.py#L128)

Decode list of parasites.

#### Signature

```python
def _parasitesDecode(self, data: bytearray) -> int: ...
```

### GimpIOBase()._parasitesEncode

[Show source in GimpIOBase.py:138](../../../gimpformats/GimpIOBase.py#L138)

Encode list of parasites.

#### Signature

```python
def _parasitesEncode(self) -> bytearray: ...
```

### GimpIOBase()._propertiesDecode

[Show source in GimpIOBase.py:517](../../../gimpformats/GimpIOBase.py#L517)

Decode a list of properties.

#### Signature

```python
def _propertiesDecode(self, ioBuf: IO) -> int: ...
```

#### See also

- [IO](./binaryiotools.md#io)

### GimpIOBase()._propertiesEncode

[Show source in GimpIOBase.py:531](../../../gimpformats/GimpIOBase.py#L531)

Encode a list of properties.

uint32  prop_type   	Type identification
uint32  len(payload)    size of payload
bytes[] payload

#### Signature

```python
def _propertiesEncode(self, enum: Enum = AllProps) -> bytearray: ...
```

#### See also

- [AllProps](./enums.md#allprops)

### GimpIOBase()._propertyDecode

[Show source in GimpIOBase.py:242](../../../gimpformats/GimpIOBase.py#L242)

Decode a single property.

#### Signature

```python
def _propertyDecode(self, prop: int, data: bytearray) -> int: ...
```

### GimpIOBase()._propertyEncode

[Show source in GimpIOBase.py:345](../../../gimpformats/GimpIOBase.py#L345)

Encode a single property.

#### Signature

```python
def _propertyEncode(self, prop: int) -> bytearray: ...
```

### GimpIOBase()._samplePointsDecode

[Show source in GimpIOBase.py:230](../../../gimpformats/GimpIOBase.py#L230)

Decode a series of points.

#### Signature

```python
def _samplePointsDecode(self, data: bytearray) -> None: ...
```

### GimpIOBase()._userUnitsDecode

[Show source in GimpIOBase.py:224](../../../gimpformats/GimpIOBase.py#L224)

Decode a set of user-defined measurement units.

#### Signature

```python
def _userUnitsDecode(self, data: bytearray) -> None: ...
```

### GimpIOBase()._vectorsDecode

[Show source in GimpIOBase.py:165](../../../gimpformats/GimpIOBase.py#L165)

Decode vectors.

#### Signature

```python
def _vectorsDecode(self, data: bytearray) -> None: ...
```

### GimpIOBase().activeVector

[Show source in GimpIOBase.py:179](../../../gimpformats/GimpIOBase.py#L179)

Get the vector that is currently active.

#### Signature

```python
@property
def activeVector(self) -> GimpVector: ...
```

#### See also

- [GimpVector](./GimpVectors.md#gimpvector)

### GimpIOBase().doc

[Show source in GimpIOBase.py:106](../../../gimpformats/GimpIOBase.py#L106)

#### Signature

```python
@property
def doc(self) -> GimpIOBase: ...
```

### GimpIOBase().expanded

[Show source in GimpIOBase.py:184](../../../gimpformats/GimpIOBase.py#L184)

Is the group layer expanded.

#### Signature

```python
@property
def expanded(self) -> bool: ...
```

### GimpIOBase().expanded

[Show source in GimpIOBase.py:189](../../../gimpformats/GimpIOBase.py#L189)

Is the group layer expanded.

#### Signature

```python
@expanded.setter
def expanded(self, expanded: bool) -> None: ...
```

### GimpIOBase().full_repr

[Show source in GimpIOBase.py:566](../../../gimpformats/GimpIOBase.py#L566)

Get a textual representation of this object.

#### Signature

```python
def full_repr(self, indent: int = 0) -> str: ...
```

### GimpIOBase().pointerSize

[Show source in GimpIOBase.py:80](../../../gimpformats/GimpIOBase.py#L80)

Determine the size of the "pointer" datatype based on the document version.

NOTE: prior to version 11, it was 32-bit,
 since then it is 64-bit, thus supporting
 larger image files

#### Signature

```python
@property
def pointerSize(self) -> int: ...
```

### GimpIOBase().root

[Show source in GimpIOBase.py:113](../../../gimpformats/GimpIOBase.py#L113)

Get the root of the file object tree (Which is the same as self.doc).

#### Signature

```python
@property
def root(self) -> GimpIOBase: ...
```

### GimpIOBase().tattoo

[Show source in GimpIOBase.py:118](../../../gimpformats/GimpIOBase.py#L118)

Gimp nomenclature for the item's unique id.

#### Signature

```python
@property
def tattoo(self) -> Any | None: ...
```

### GimpIOBase().tattoo

[Show source in GimpIOBase.py:123](../../../gimpformats/GimpIOBase.py#L123)

Gimp nomenclature for the item's unique id.

#### Signature

```python
@tattoo.setter
def tattoo(self, tattoo: Any | None) -> None: ...
```



## GimpUserUnits

[Show source in GimpIOBase.py:643](../../../gimpformats/GimpIOBase.py#L643)

User-defined measurement units.

#### Signature

```python
class GimpUserUnits:
    def __init__(self) -> None: ...
```

### GimpUserUnits().__str__

[Show source in GimpIOBase.py:690](../../../gimpformats/GimpIOBase.py#L690)

Get a textual representation of this object.

#### Signature

```python
def __str__(self) -> str: ...
```

### GimpUserUnits().decode

[Show source in GimpIOBase.py:655](../../../gimpformats/GimpIOBase.py#L655)

Decode a byte buffer.

#### Arguments

----
 - `data` *bytearray* - data buffer to decode
 - `index` *int, optional* - index within the buffer to start at]. Defaults to 0.

#### Returns

-------
 - `int` - offset

#### Signature

```python
def decode(self, data: bytearray, index: int = 0) -> int: ...
```

### GimpUserUnits().encode

[Show source in GimpIOBase.py:678](../../../gimpformats/GimpIOBase.py#L678)

Convert this object to raw bytearray.

#### Signature

```python
def encode(self) -> bytearray: ...
```

### GimpUserUnits().full_repr

[Show source in GimpIOBase.py:694](../../../gimpformats/GimpIOBase.py#L694)

Get a textual representation of this object.

#### Signature

```python
def full_repr(self, indent: int = 0) -> str: ...
```



## camel_to_pascal_with_spaces

[Show source in GimpIOBase.py:32](../../../gimpformats/GimpIOBase.py#L32)

#### Signature

```python
def camel_to_pascal_with_spaces(val: str) -> str: ...
```