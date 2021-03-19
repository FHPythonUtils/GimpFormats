# GimpGplPalette

> Auto-generated documentation for [gimpformats.GimpGplPalette](../../gimpformats/GimpGplPalette.py) module.

Pure python implementation of the gimp gpl palette format.

- [Gimpformats](../README.md#gimpformats-index) / [Modules](../README.md#gimpformats-modules) / [gimpformats](index.md#gimpformats) / GimpGplPalette
    - [GimpGplPalette](#gimpgplpalette)
        - [GimpGplPalette().\_\_eq\_\_](#gimpgplpalette__eq__)
        - [GimpGplPalette().\_\_repr\_\_](#gimpgplpalette__repr__)
        - [GimpGplPalette().decode](#gimpgplpalettedecode)
        - [GimpGplPalette().encode](#gimpgplpaletteencode)
        - [GimpGplPalette().load](#gimpgplpaletteload)
        - [GimpGplPalette().save](#gimpgplpalettesave)

## GimpGplPalette

[[find in source code]](../../gimpformats/GimpGplPalette.py#L9)

```python
class GimpGplPalette():
    def __init__(fileName: BytesIO | str | None = None):
```

Pure python implementation of the gimp gpl palette format.

### GimpGplPalette().\_\_eq\_\_

[[find in source code]](../../gimpformats/GimpGplPalette.py#L98)

```python
def __eq__(other: GimpGplPalette):
```

Perform a comparison.

### GimpGplPalette().\_\_repr\_\_

[[find in source code]](../../gimpformats/GimpGplPalette.py#L83)

```python
def __repr__():
```

Get a textual representation of this object.

### GimpGplPalette().decode

[[find in source code]](../../gimpformats/GimpGplPalette.py#L35)

```python
def decode(data: str) -> None:
```

Decode a byte buffer.

#### Arguments

- `data` - data buffer to decode

### GimpGplPalette().encode

[[find in source code]](../../gimpformats/GimpGplPalette.py#L57)

```python
def encode():
```

Encode to a raw data stream.

### GimpGplPalette().load

[[find in source code]](../../gimpformats/GimpGplPalette.py#L20)

```python
def load(fileName: BytesIO | str):
```

Load a gimp file.

#### Arguments

- `fileName` - can be a file name or a file-like object

### GimpGplPalette().save

[[find in source code]](../../gimpformats/GimpGplPalette.py#L74)

```python
def save(fileName: str | BytesIO):
```

Save this gimp image to a file.