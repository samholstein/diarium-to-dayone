# Diarium to Day One Converter

This Python script converts Diarium JSON exports to Day One JSON format, including support for media files.

## Features

- ✅ Converts Diarium JSON entries to Day One format
- ✅ Preserves entry dates and times
- ✅ Converts HTML content to Day One rich text format
- ✅ Handles location data
- ✅ Processes weather data (sunrise/sunset, moon phases)
- ✅ Supports media file attachments
- ✅ Creates a Day One JSON file
- ✅ Maintains tags and metadata

## Requirements

- Python 3.6+
- Required packages (install via `pip install -r requirements.txt`):
  - beautifulsoup4
  - lxml

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Conversion

```bash
python diarium-to-dayone.py diarium-json/diarium-json.json dayone_import.json
```

This will create a `dayone_import.json` file in Day One format.

### Import into Day One

1. **Create the JSON file:**
   ```bash
   python diarium-to-dayone.py diarium-json/diarium-json.json dayone_import.json
   ```

2. **Zip the JSON file:**
   ```bash
   zip dayone_import.zip dayone_import.json
   ```

3. **Import into Day One:**
   - Open Day One on your Mac
   - Go to **File > Import > Import from JSON**
   - Select the `dayone_import.zip` file
   - Day One will import all entries

## File Structure

The script expects the following structure:
```
diarium-to-dayone/
├── diarium-to-dayone.py
├── diarium-json/
│   ├── diarium-json.json    # Your Diarium export
│   └── media/               # Media files (optional)
│       └── YYYY-MM-DD_*/    # Date-based folders
└── requirements.txt
```

## Output Format

The script creates a JSON file containing:
- `metadata` - Version information
- `entries` - Array of Day One journal entries

## Data Mapping

| Diarium Field | Day One Field | Notes |
|---------------|---------------|-------|
| `date` | `creationDate` | Converted to UTC format |
| `html` | `richText` | Converted to Day One rich text format |
| `heading` + `html` | `text` | Combined plain text |
| `location` | `location` | Preserved as-is |
| `sun` + `lunar` | `weather` | Parsed for sunrise/sunset and moon phases |
| `tags` | `tags` | Preserved as-is |
| Media files | `media` | Referenced in entries |

## Troubleshooting

### Common Issues

1. **Media files not found**: Ensure your media files are in the `diarium-json/media/` directory
2. **Date parsing errors**: The script handles various Diarium date formats automatically
3. **Large files**: The script processes entries in batches and shows progress

### Error Messages

- `Warning: Media directory not found` - This is normal if you don't have media files
- `Failed to add media` - Individual media files that couldn't be processed (conversion continues)

## Example

```bash
# Convert your Diarium export
python diarium-to-dayone.py diarium-json/diarium-json.json dayone_import.json

# Create ZIP for Day One import
zip dayone_import.zip dayone_import.json

# Import into Day One
# 1. Open Day One
# 2. File > Import > Import from JSON
# 3. Select dayone_import.zip
```

## License

This script is provided as-is for converting Diarium exports to Day One format. 