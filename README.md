Here’s a revised approach for a "Getting Started" manual in `readme.md`, structured to guide users step-by-step from simple to advanced usage:

---

# TokenPDF: Generate Printable RPG Tokens with Ease

**TokenPDF** is a lightweight Python library for creating printable PDF files containing RPG tokens. It simplifies the process of generating tokens for monsters, characters, and other entities in tabletop role-playing games (specifically Dungeons & Dragons and similar games).

![Example output](images/example_output.png)  
*Example of generated tokens.*

---

## Getting Started

### Installation

TokenPDF will soon be available on PyPI. For now, clone the repository and install its dependencies:

```bash
git clone https://github.com/Dormat2/tokenpdf.git
cd tokenpdf
pip install -r requirements.txt
```

---

### Command-Line Interface

The library provides a simple command-line tool:

```bash
python -m tokenpdf <config_files> [-o OUTPUT] [-v] [-s]
```

- `config_files`: One or more configuration files in TOML, JSON, YAML, or INI format. If omitted, `example.toml` is used.
- `-o OUTPUT`: The output PDF file (default: `output.pdf`).
- `-v`: Enable verbose output.
- `-s`: Silence most output.

Example usage:

```bash
python -m tokenpdf example.toml -o my_tokens.pdf -v
```

---

## Writing Configuration Files

Configurations define your tokens, page settings, and more. Let's start with a simple example.

### Minimal Configuration: Single Token

#### TOML Example

```toml
output = "single_token.pdf"

[monsters.circle_token]
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

#### 1. **Adding Multiple Tokens**
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

---

#### 2. **Customizing Token Appearance**
Add margins and scaling to tokens:

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

---

## Global Settings

Customize the entire output, page, and layout behavior. Here’s how to configure global settings.

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
page_size = "A4"
orientation = "portrait"
margin = 0.05
```

**JSON**
```json
{
  "page_size": "A4",
  "orientation": "portrait",
  "margin": 0.05
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

---

### Advanced Examples

#### Mixed Token Types

**TOML**
```toml
[monsters.goblins]
name = "Goblins"
size = "Small"
image_url = "https://picsum.photos/300"
tokens = [
    { type = "circle", size = "small", count = 10 },
    { type = "standing", size = "small", count = 5 }
]
```

**JSON**
```json
{
  "monsters": {
    "goblins": {
      "name": "Goblins",
      "size": "Small",
      "image_url": "https://picsum.photos/300",
      "tokens": [
        { "type": "circle", "size": "small", "count": 10 },
        { "type": "standing", "size": "small", "count": 5 }
      ]
    }
  }
}
```

---

### Screenshots

- Example configuration:  
  ![Example Configuration Screenshot](images/config_example.png)

- Generated PDF:  
  ![Generated PDF Screenshot](images/output_example.png)

---

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests via GitHub.  

