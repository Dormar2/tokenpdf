# Monsters Configuration Section
This page describes the structure of the `monsters` configuration key in the `tokenpdf` configuration file. The `monsters` key defines the monsters, their tokens, and their appearance in the PDF output.

## Monster Definition
Monsters are defined as sub-keys of the `monsters` key. The key is the monster id. The value is a dictionary of the monster's properties.

for example:
```toml

[monsters.ape]
name = "Ape"
size = "Medium"
type = "Beast"
images_url = ["./ape1.webp", "./ape2.webp", "./ape3.jpg"]
tokens = [
    { type = "standing", size = "medium", count = 5}
] 
```
```json
{
  "monsters": {
    "ape": {
      "name": "Ape",
      "size": "Medium",
      "type": "Beast",
      "images_url": ["./ape1.webp", "./ape2.webp", "./ape3.jpg"],
      "tokens": [
        { "type": "standing", "size": "medium", "count": 5}
      ]
    }
  }
}
```

### Monster Properties
The following properties are supported for each monster:
- `name`: The name of the monster. Currently unused.
- `size`: The size of the monster. This can be a string (e.g., "Medium") or a tuple of two floats (width, height) in mm. When a string is used, the system is used to determine the resulting size. The system defines the supported sizes and their dimensions. For the default system (D&D 5e), the sizes are: "Fine", "Diminutive", "Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan", "Colossal", and "ColossalPlus1" up to "ColossalPlus16". (Default: "Medium")
- `type`: The type of the monster. Currently unused.
- `image_url`: The URL or path to monster's image. If a URL, the image will be downloaded. This value or `images_url` **is required**.
- `images_url`: An alternative to `image_url` that allows multiple images for the monster. The images are used in the order they are defined. If the number of tokens exceeds the number of images, the images are repeated. If `randomize_images` is true (Default: False), the images are instead sampled from this list for each token (with replacement). 

### Token Definitions
For each monster, a `tokens` key can be provided, to define tokens for the monster.
The value is a list of token definitions. Each token definition can have the following properties:
- `type`: The type of the token. The types supported are:
    - `standing`: A standing token.
    - `circle`: A circular token.
- `size`: See `size` in the monster properties above.
- `border_width`: The width of the token's border in mm. (Default: 0)
- `scale`: The scale of the token's size. Applied as a multiplier to the token's size after applying the system's sizing. (Default: 1)
- `scale_rho`: If present and not 0, the scale is determined by a log-normal distribution around `scale`, with a standard deviation of `scale_rho`. Sampled individually for each token instance. (Default: 0)
- `rect_border_thickness`: The thickness of the rectangle border in mm. (Default: 0 for circle tokens, 1 for standing tokens)
- `rect_border_color`: The color of the rectangle border. Can be a string (e.g., `"black"`) or a list of 3 integers (e.g., [0, 0, 0]) for RGB values. (Default: `"black"`)
- `rect_border_style`: The style of the rectangle border. Can be any combination of "solid", "dot", and "dash" separated by "-" (e.g., "solid-dot-dash"). See reportlab documentation for reference. (Default: `"dot-dash"`)
- Other token-type specific properties. See [Standing Token](#standing-token) and [Circle Token](#circle-token) below for more information.

### Token Creation
For each token definition, `count` tokens are created as follows:
1. The `token` key (if present) in the configuration's root is used as the default token properties.
2. This dictionary is overridden (merged) with the monster's properties (other than `tokens`)
3. This dictionary is overridden with the specific token definition properties.

In this way, one can define a default token configuration for all monsters (under the root `token` key), default token configurations for all tokens of a monster (under the monster's key), and specific token configurations for each token of a monster.

### Standing Token
This is the main token type. It creates a "Standing" token, with is a rectangle that has room for two copies of the image, one on each side of the halfway line. Space is added at each end for the token's "stand". The token is meant to be cut out and folded along the halway line (hill-fold) and along the stand lines (valley-folds).
(#TODO: Add images)

The following properties are standing-token specific:
- `keep_aspect_ratio`: If false, the image may be stretched to fit the rectangle area (Default: true)


### Examples

```toml


[monsters.ape]
name = "Ape"
size = "Medium"
type = "Beast"
images_url = ["./ape1.webp", "./ape2.webp", "./ape3.jpg"]
tokens = [
    { type = "standing", size = "medium", count = 5}
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

[monsters.shinebright]
name = "Finethir Shinebright"
size = "Medium"
type = "Humanoid"
image_url = "./Shinebright.png"
tokens = [
    { type = "standing", size = "medium", count = 1}
]
```

```json

{
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
    "shinebright": {
      "name": "Finethir Shinebright",
      "size": "Medium",
      "type": "Humanoid",
      "image_url": "./Shinebright.png",
      "tokens": [
        { "type": "standing", "size": "medium", "count": 1}
      ]
    }
  }
}
```
