# RPG System Configurations
This page describes the structure of the `system` configuration files and references to it in the `tokenpdf` configuration file. The `system` key defines the default token sizes and other system-specific settings.

## System Definition
Systems are defined by dedicated configuration files (any that are supported by `tokenpdf`). 
Configuration files located in the `tokenpdf/data/systems` subdirectory of the `tokenpdf` installation directory are automatically loaded. Other systems can be loaded by specifying the path to the configuration file in the `system` key of the main configuration file.
Otherwise, the `system` key references the name of the system.

### System Properties
The following properties are supported for each system:
- `name`: The name of the system. This is used to reference the system in the main configuration file. (Example: "D&D 5e")
- `token_sizes`: A dictionary of the supported sizes and their dimensions. The keys are the size names from the system(e.g., "Medium"), and the values are tuples of two floats (width, height) in the in-game default units (see below).
- `cell_size`: A dictionary with the following properties:
    - `unit`: The name or abbrivation of the unit used in the system (e.g., "ft", "m", "sq", "hex").
    - `mm`: The size of a cell in mm **on page**. For example, for D&D 5e, a cell representing a 5ft in-game square is usually 1inch x 1inch, which is 25.4mm x 25.4mm.
    - `world`: The size of a cell in the in-game default units. For example, for D&D 5e, a cell usually represents a 5ft x 5ft square.

Note: All the above numeric pair values can be specified as a signle number, which will be used for both dimensions.

### Example System Configuration (D&D 5e)
```toml

name = "D&D 5e"

[token_sizes]
    # The size of the token in feet (world units)
    Fine = 0.5
    Diminutive = 1
    Tiny = 2.5
    Small = 4
    Medium = 5
    Large = 10
    Huge = 15
    Gargantuan = 20
    Colossal = 30
    # From: https://dungeons.fandom.com/wiki/SRD:Table_of_Creature_Size_and_Scale
    ColossalPlus1 = 40
    ColossalPlus2 = 50
    ColossalPlus3 = 70
    ColossalPlus4 =  90
    ColossalPlus5 =  110
    ColossalPlus6 =  150
    ColossalPlus7 =  190
    ColossalPlus8 =  230
    ColossalPlus9 =  310
    ColossalPlus10 = 390
    ColossalPlus11 = 470
    ColossalPlus12 = 630
    ColossalPlus13 = 790
    ColossalPlus14 = 950
    ColossalPlus15 = 1270
    ColossalPlus16 = 1590


[cell_size]
    mm = 25.4 # Paper cell size in mm: 1x1 inch
    world = 5 # World cell size in "system world" units: 5
    unit = "ft" # "System world" units  

```

```json
{
    "name": "D&D 5e",
    "token_sizes": {
        "Fine": 0.5,
        "Diminutive": 1,
        "Tiny": 2.5,
        "Small": 4,
        "Medium": 5,
        "Large": 10,
        "Huge": 15,
        "Gargantuan": 20,
        "Colossal": 30,
        "ColossalPlus1": 40,
        "ColossalPlus2": 50,
        "ColossalPlus3": 70,
        "ColossalPlus4": 90,
        "ColossalPlus5": 110,
        "ColossalPlus6": 150,
        "ColossalPlus7": 190,
        "ColossalPlus8": 230,
        "ColossalPlus9": 310,
        "ColossalPlus10": 390,
        "ColossalPlus11": 470,
        "ColossalPlus12": 630,
        "ColossalPlus13": 790,
        "ColossalPlus14": 950,
        "ColossalPlus15": 1270,
        "ColossalPlus16": 1590
    },
    "cell_size": {
        "mm": 25.4,
        "world": 5,
        "unit": "ft"
    }
}