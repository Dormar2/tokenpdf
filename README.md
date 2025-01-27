# TokenPDF: Generate printable PDFs for RPG tokens and map

**TokenPDF** is a lightweight Python library for creating printable PDF files containing RPG tokens and (possibly large) maps. It simplifies the process of generating monster-tokens, and fragmenting maps into printable pages, while minimizing the number of papers required.
The library is fully configureable.

![Example output](images/example_output.png)  

---
## Changelog

See the [Changelog](CHANGELOG.md) for details on recent changes.

## Getting Started

### Installation

#### From PyPI

```bash
pip install tokenpdf
```

#### From source

```bash
git clone https://github.com/Dormat2/tokenpdf.git
cd tokenpdf
pip install -r requirements.txt
```

---

### Command-Line Interface

The library provides both a command-line interface and a Python API. The CLI is the easiest way to get started.

```bash
python -m tokenpdf <config_files> [-o OUTPUT] [-v] [-s]
```

- `config_files`: One or more configuration files in TOML, JSON, YAML, or INI format. See examples below, or [Configuration Reference](CONFIGURATION_REFERENCE.md) for more details. Can only be omitted if `-e` flag is used.
- `-e`: Use the example configuration file (`tokenpdf/data/example.toml`).
- `-o OUTPUT`: The output PDF file (default: `output.pdf`). If ommited, the output name is derived from the first configuration file.
- `-v`: Enable verbose output.
- `-s`: Silence most output.

Example usage:

```bash
python -m tokenpdf example.toml -o my_tokens.pdf -v
```

---

## Writing Configuration Files

Configurations define your monsters, their tokens, the maps, and the pdf layout and generation process. 

### Minimal Configuration: Single Token

#### TOML Example

```toml
output = "single_token.pdf"

[monsters.circle]
name = "Circle Token"
size = "Medium"
image_url = "https://picsum.photos/200"
tokens = [
    { type = "circle", size = "medium", count = 1 }
]
```

#### JSON Example

```json
{
  "output": "single_token.pdf",
  "monsters": {
    "circle_token": {
      "name": "Circle Token",
      "size": "Medium",
      "image_url": "https://picsum.photos/200",
      "tokens": [
        { "type": "circle", "size": "medium", "count": 1 }
      ]
    }
  }
}
```

---

### Adding Features Step-by-Step

#### 1. **Multiple Tokens for a single monster**
Add multiple tokens for the same monster:

**TOML Example**
```toml
[monsters.circle_token]
name = "Circle Token"
size = "Medium"
image_url = "https://picsum.photos/200"
tokens = [
    { type = "circle", size = "medium", count = 5 }
]
```

**JSON Example**
```json
{
  "monsters": {
    "circle_token": {
      "name": "Circle Token",
      "size": "Medium",
      "image_url": "https://picsum.photos/200",
      "tokens": [
        { "type": "circle", "size": "medium", "count": 5 }
      ]
    }
  }
}
```

Add a standing token for the same monster:

**TOML Example**
```toml
[monsters.circle_token]
name = "Circle Token"
size = "Medium"
image_url = "https://picsum.photos/200"
tokens = [
    { type = "circle", size = "small", count = 5 },
    { type = "standing", size = "medium", count = 5 }
]
```
Note: The `size` field is used to determine the token's dimensions in relation to the page size and the system (default: D&D5e) grid sizing (can be overriden). The size can be specified in the monster's configuration, and/or overriden in the token's configuration.

---

#### 2. **Customizing Token Appearance**
Scaling:

**TOML Example**
```toml
[monsters.circle_token]
name = "Circle Token"
size = "Medium"
image_url = "https://picsum.photos/200"
tokens = [
    { type = "circle", size = "medium", count = 5, scale = 1.1, scale_rho = 0.1 }
]
```

**JSON Example**
```json
{
  "monsters": {
    "circle_token": {
      "name": "Circle Token",
      "size": "Medium",
      "image_url": "https://picsum.photos/200",
      "tokens": [
        { "type": "circle", "size": "medium", "count": 5, "scale": 1.1, "scale_rho": 0.1 }
      ]
    }
  }
}
```
In this example, the `scale` field scales the token's size. The scale is determined by a log-normal distribution around `1.1`, with a standard deviation of `0.1`. This provides a more natural variation in token sizes. Omitting `scale_rho` will set the scale to a fixed value (`1.1`)

---

## Global Settings

Customize the entire output, page, and layout behavior. Here’s how to configure some global settings.

#### **1. Output File**
Specify the name of the PDF file:

**TOML**
```toml
output = "my_custom_tokens.pdf"
```

**JSON**
```json
{
  "output": "my_custom_tokens.pdf"
}
```

---

#### **2. Page Settings**
Define the paper size, orientation, and margins:

**TOML**
```toml
# General configuration
output = "wsc_{ps}.pdf"
verbose = true
system = "D&D 5e"
compress = true

# Paper settings
page_size = ["A2", "A3", "A4"]
orientation = "portrait"
margin = 0.05
optimize_images_for_dpi = 100
optimize_images_for_quality = 80

# Layout settings
rotation = true
```

**JSON**
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
  "rotation": true
}
```

---

#### **3. Layout Options**
Enable token rotation for better page utilization:

**TOML**
```toml
rotation = true
```

**JSON**
```json
{
  "rotation": true
}
```

#### **4. Reference**
For a full reference of all available settings, see the [Configuration Reference](CONFIGURATION_REFERENCE.md).

---

### Screenshots

- Example configuration:  
  ![Example Configuration Screenshot](images/config_example.png)

- Generated PDF:  
  ![Generated PDF Screenshot](images/output_example.png)

---

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests via GitHub.  

