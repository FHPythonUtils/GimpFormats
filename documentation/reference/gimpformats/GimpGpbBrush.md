# Gimpgpbbrush

[Gimpformats Index](../README.md#gimpformats-index) / [Gimpformats](./index.md#gimpformats) / Gimpgpbbrush

> Auto-generated documentation for [gimpformats.GimpGpbBrush](../../../gimpformats/GimpGpbBrush.py) module.

- [Gimpgpbbrush](#gimpgpbbrush)
  - [GimpGpbBrush](#gimpgpbbrush)
    - [GimpGpbBrush().__repr__](#gimpgpbbrush()__repr__)
    - [GimpGpbBrush().__str__](#gimpgpbbrush()__str__)
    - [GimpGpbBrush().decode](#gimpgpbbrush()decode)
    - [GimpGpbBrush().encode](#gimpgpbbrush()encode)
    - [GimpGpbBrush().load](#gimpgpbbrush()load)
    - [GimpGpbBrush().save](#gimpgpbbrush()save)

## GimpGpbBrush

[Show source in GimpGpbBrush.py:13](../../../gimpformats/GimpGpbBrush.py#L13)

Pure python implementation of the OLD gimp gpb brush format.

See:
 https://gitlab.gnome.org/GNOME/gimp/blob/master/devel-docs/vbr.txt

#### Signature

```python
class GimpGpbBrush:
    def __init__(self, fileName: BytesIO | str) -> None: ...
```

### GimpGpbBrush().__repr__

[Show source in GimpGpbBrush.py:74](../../../gimpformats/GimpGpbBrush.py#L74)

Get a textual representation of this object.

#### Signature

```python
def __repr__(self, indent: int = 0) -> str: ...
```

### GimpGpbBrush().__str__

[Show source in GimpGpbBrush.py:70](../../../gimpformats/GimpGpbBrush.py#L70)

Get a textual representation of this object.

#### Signature

```python
def __str__(self) -> str: ...
```

### GimpGpbBrush().decode

[Show source in GimpGpbBrush.py:43](../../../gimpformats/GimpGpbBrush.py#L43)

Decode a byte buffer.

#### Arguments

----
 - `data` *bytes* - data to decode
 - `index` *int, optional* - index to start from. Defaults to 0.

#### Returns

-------
 - `int` - pointer

#### Signature

```python
def decode(self, data: bytes, index: int = 0) -> int: ...
```

### GimpGpbBrush().encode

[Show source in GimpGpbBrush.py:59](../../../gimpformats/GimpGpbBrush.py#L59)

Encode this object to bytes.

#### Signature

```python
def encode(self) -> bytes: ...
```

### GimpGpbBrush().load

[Show source in GimpGpbBrush.py:35](../../../gimpformats/GimpGpbBrush.py#L35)

Load a gimp file.

#### Arguments

- `fileName` - can be a file name or a file-like object

#### Signature

```python
def load(self, fileName: BytesIO | str) -> None: ...
```

### GimpGpbBrush().save

[Show source in GimpGpbBrush.py:66](../../../gimpformats/GimpGpbBrush.py#L66)

Save this gimp image to a file.

#### Signature

```python
def save(self, tofileName: str | BytesIO | None = None) -> None: ...
```