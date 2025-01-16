# Map Fragmentation Tokens
This page describes the structure of the `maps` configuration key in the `tokenpdf` configuration file. The `maps` key defines the maps, their fragmentation into tokens, and their appearance in the PDF output.

A map is an image, typically larger than a page, that needs to be split into smaller pieces for printing. The map is divided into grid, and each cell in the grid is a token of page size or smaller. The tokens are then placed in the PDF output according to the layout algorithm (possibly alongside monster tokens).

## Map Definition
Maps are defined as sub-keys of the `maps` key. The key is the map id. The value is a dictionary of the map's properties.

for example:
```toml
[maps.street]
name = "Town Street"
border_margin = 0
text_margin = 0.05
image_url = "../Maps/TownStreet.webp"
grid = [24, 32]
```
```json
{
  "maps": {
    "street": {
      "name": "Town Street",
      "border_margin": 0,
      "text_margin": 0.05,
      "image_url": "../Maps/TownStreet.webp",
      "grid": [24, 32]
    }
  }
}
```

### Map Properties
The following properties are supported for each map:
- `name`: The name of the map. Will be used if `text_margin` is non-zero.
- `border_margin`: The margin around the map in page ratio, i.e. a number between 0 and 1 that is multiplied by the page's smallest dimension. (Default: 0)
- `text_margin`: The margin below the map for text, in page ratio (see `border_margin`). If present, the map's name and the fragmentation coordinates (in terms of page-sized grid cells) are printed below the map. For example, "Town Street: 0,3" (Default: 0)
- `image_url`: The URL or path to the map's image. If a URL, the image will be downloaded. This value is **required**.
- `add_grid`: The map's system grid is added to the map as a visual aid (see below for grid sizing). (Default: false)

#### Sizing
The map's grid (in term of RPG system cells) is determined in one of two ways:
- `grid`: A list of two integers `[rows, cols]` that define the grid size.
- `dpi` or `dpmm`: The DPI or DPMM of the map. The grid size is determined by the map's dimensions divided by the DPI or DPMM (with proper unit conversion). If `grid` is present, it takes precedence.
**At least one of `grid` or `dpi`/`dpmm` is required.**



