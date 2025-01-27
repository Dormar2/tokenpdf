# Configuration Input
This page describes the structure of configuration file inputs for `tokenpdf`.
The configuration file is the main input to the `tokenpdf` program. It defines the monsters, their tokens, the maps, and the pdf layout and generation process.

## Multiple Configuration Files
The tokenpdf script (and class) can accept multiple configuration files, which are recursively merged into a single configuration.

## Relative Paths
All paths in the configuration file are relative to the configuration file's location. If multiple configuration files are used, the paths are relative to the first (TODO: check, last?) configuration file's location.

## Configuration File Format
The configuration file can be in TOML, JSON, YAML, or INI (ConfigParser) format. The file extension determines the format. Different configuration files can be in different formats (including imports)

## Importing
A configuration file can import other configuration files. There are two ways to import:
1. `@import: <anything>` as a key. The value is the path to the configuration file to import. The imported configuration is merged into the key's parent dictionary.
2. `@import: <path>` as a value. The path is the configuration file to import. The imported configuration is set as the value of the key.

## Configuration Reference
All values in the configuration file are optional unless otherwise specified.

The root node of the configuration file supports the following keys:

### Output
- `output`: The output PDF file (default: `output.pdf`). Can be overridden with the `-o` command line argument.
 - The following variables can be used in the filename:
    - `{ps}`: The page size (e.g., "letter", "A4") - taken from the `page_size` key.
- `verbose`: Enable verbose output. Can be overridden with the `-v` command line argument. (Default: false)
- `optimize_pdf_for_dpmm`: The pdf images will be resampled to this DPMM (dots per mm) before being embedded in the pdf. If 0, no resampling is done. (Default: 0)
- `optimize_pdf_for_dpi`: An alternative to `optimize_pdf_for_dpmm` to specify with units of `DPI` instead of `DPMM`. (Default: 0)
- `optimize_pdf_for_quality`: The PNG quality of the images in the pdf. A number between 0 and 100. If 0, the default quality is used. (Default: 0)
- `compress`: Compress the PDF output as post-processing. (Default: false)

### Page
- `page_size`: The size of the PDF page. Can be a string (e.g., "letter", "A4") or a tuple of two floats (width, height) in mm. (Default: "A4")
- `orientation`: The orientation of the PDF page. Can be "portrait" or "landscape". (Default: "portrait")
- `margin`: The page margin in mm (Default: 0).

### Layout
For more information, see [Layout Algorithms](layout.md).
- `layout`: The layout algorithm (or algorithm combination) to use. Options are:
 - `rectpack_best`: A default combination of rectpack algorithms that produces the best results. (Default)
 - `rectpack`: Any of the rectpack algorithms. See [Layout Algorithms](layout.md).
 - `greedy`: A greedy algorithm that places tokens in the order they are defined in the configuration file.
 - `all`: Best result from applying all available layout algorithms.
- `rotation`: Allow rotation of tokens to fit better in the layout. (Default: false)
- `system`: The RPG system to use. This is used to determine the default token sizes and other system-specific settings. For more information, see [System Configuration](systems.md). (Default: "D&D 5e")


### Sub-Configurations
The following keys are separate sections, that are documented in their respective pages:
- `monsters`: Monster definitions and their tokens. See [Monsters](monsters.md).
- `maps`: Map fragmentation tokens. See [Maps](maps.md).
- `token`: Default token key/values. See [Monsters](monsters.md).
- `map`: Default map key/values. See [Maps](maps.md).

## Example Configuration
```toml

# General configuration
output = "wsc_{ps}.pdf"
verbose = true
system = "D&D 5e"
compress= true

# Paper settings
page_size = ["A2", "A3", "A4"]
orientation = "portrait"
margin = 0.05
optimize_images_for_dpi = 100
optimize_images_for_quality = 80

# Layout settings
rotation = true


[map]
overlap_margin = 0.5
[token]
standing_margin = 0.05


[maps.street]
name = "Town Street"
border_margin = 0
text_margin = 0.05
image_url = "../Maps/TownStreet.webp"
grid = [24, 32]

[maps.hideout]
name = "Hideout"
image_url = "../Maps/Hideout.jpg"
dpi = 100
add_grid = true
border_margin = 0
text_margin = 0.05

[monsters.ape]
name = "Ape"
size = "Medium"
type = "Beast"
images_url = ["./ape1.webp", "./ape2.webp", "./ape3.jpg"]
tokens = [
    { type = "standing", size = "medium", count = 5}
]

[monsters.guz]
type = "Humanoid"
name = "Guz"
size = "Medium"
image_url = "./Guz.jpg"
tokens = [
    { type = "standing", size = "medium", count = 1}
]

[monsters.sheep]
name = "Sheep"
size = "Medium"
type = "Beast"
image_url = "./sheep.png"
tokens = [
    { type = "standing", size = "medium", count = 1}
]

[monsters.brown_bear]
name = "Brown Bear"
size = "Large"
type = "Beast"
images_url = ["./brownbear.png", "./brownbear2.png"]
tokens = [
    { type = "standing", size = "large", count = 2},
    { type = "standing", size = "huge", count = 1}
]

[monsters.noke]
name = "Carmen Noke"
size = "Medium"
type = "Humanoid"
image_url = "./Noke.png"
tokens = [
    { type = "standing", size = "medium", count = 1}
]

[monsters.shinebright]
name = "Finethir Shinebright"
size = "Medium"
type = "Humanoid"
image_url = "./Shinebright.png"
tokens = [
    { type = "standing", size = "medium", count = 1}
]

[monsters.wolf]
name = "Wolf"
size = "Medium"
type = "Beast"
images_url = ["./wolf1.webp", "./wolf2.jpg"]
tokens = [
    { type = "standing", size = "medium", count = 3}
]

[monsters.bed_dragon]
name = "Bed Dragon"
size = "Large"
type = "Dragon"
images_url = ["./bed_dragon1.png", "./bed_dragon2.png"]
tokens = [
    { type = "standing", size = "large", count = 2},
    #{ type = "circle", size = "large", count = 2}
]

```

```json
{
  "output": "wsc_{ps}.pdf",
  "verbose": true,
  "system": "D&D 5e",
  "compress": true,
  "page_size": ["A2", "A3", "A4"],
  "orientation": "portrait",
  "margin": 0.05,
  "optimize_images_for_dpi": 100,
  "optimize_images_for_quality": 80,
  "rotation": true,
  "map": {
    "overlap_margin": 0.5
  },
  "token": {
    "standing_margin": 0.05
  },
  "maps": {
    "street": {
      "name": "Town Street",
      "border_margin": 0,
      "text_margin": 0.05,
      "image_url": "../Maps/TownStreet.webp",
      "grid": [24, 32]
    },
    "hideout": {
      "name": "Hideout",
      "image_url": "../Maps/Hideout.jpg",
      "dpi": 100,
      "add_grid": true,
      "border_margin": 0,
      "text_margin": 0.05
    }
  },
  "monsters": {
    "ape": {
      "name": "Ape",
      "size": "Medium",
      "type": "Beast",
      "images_url": ["./ape1.webp", "./ape2.webp", "./ape3.jpg"],
      "tokens": [
        { "type": "standing", "size": "medium", "count": 5}
      ]
    },
    "guz": {
      "type": "Humanoid",
      "name": "Guz",
      "size": "Medium",
      "image_url": "./Guz.jpg",
      "tokens": [
        { "type": "standing", "size": "medium", "count": 1}
      ]
    },
    "sheep": {
      "name": "Sheep",
      "size": "Medium",
      "type": "Beast",
      "image_url": "./sheep.png",
      "tokens": [
        { "type": "standing", "size": "medium", "count": 1}
      ]
    },
    "brown_bear": {
      "name": "Brown Bear",
      "size": "Large",
      "type": "Beast",
        "images_url": ["./brownbear.png", "./brownbear2.png"],
        "tokens": [
          { "type": "standing", "size": "large", "count": 2},
          { "type": "standing", "size": "huge", "count": 1}
        ]
    },
    "noke": {
      "name": "Carmen Noke",
      "size": "Medium",
      "type": "Humanoid",
      "image_url": "./Noke.png",
      "tokens": [
        { "type": "standing", "size": "medium", "count": 1}
      ]
    },
    "shinebright": {
      "name": "Finethir Shinebright",
      "size": "Medium",
      "type": "Humanoid",
      "image_url": "./Shinebright.png",
      "tokens": [
        { "type": "standing", "size": "medium", "count": 1}
      ]
    },
    "wolf": {
      "name": "Wolf",
      "size": "Medium",
      "type": "Beast",
      "images_url": ["./wolf1.webp", "./wolf2.jpg"],
      "tokens": [
        { "type": "standing", "size": "medium", "count": 3}
      ]
    },
    "bed_dragon": {
      "name": "Bed Dragon",
      "size": "Large",
      "type": "Dragon",
      "images_url": ["./bed_dragon1.png", "./bed_dragon2.png"],
      "tokens": [
        { "type": "standing", "size": "large", "count": 2},
        { "type": "circle", "size": "large", "count": 2}
      ]
    }
    }
}
```