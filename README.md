# Diarium to Day One Converter

This Python script converts Diarium JSON exports to Day One JSON format with proper timezone handling.

## Features

- ✅ Converts Diarium JSON entries to Day One format
- ✅ Preserves entry dates and times with correct timezone conversion (EDT to UTC)
- ✅ Converts HTML content to Day One rich text format
- ✅ Handles location data
- ✅ Processes weather data (sunrise/sunset, moon phases)
- ✅ Maintains tags and metadata
- ✅ Creates a Day One JSON file ready for import

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

2. **Create import package:**
   ```bash
   mkdir dayone_import_package
   cp dayone_import.json dayone_import_package/Journal.json
   zip -r dayone_import_package.zip dayone_import_package/
   ```

3. **Import into Day One:**
   - Open Day One on your Mac
   - Go to **File > Import > Import from ZIP**
   - Select the `dayone_import_package.zip` file
   - Day One will import all entries

## File Structure

The script expects the following structure:
```
diarium-to-dayone/
├── diarium-to-dayone.py
├── diarium-json/
│   └── diarium-json.json    # Your Diarium export
└── requirements.txt
```

## Output Format

The script creates a JSON file containing:
- `metadata` - Version information
- `entries` - Array of Day One journal entries

## Data Mapping

| Diarium Field | Day One Field | Notes |
|---------------|---------------|-------|
| `date` | `creationDate` | Converted from EDT to UTC format |
| `html` | `richText` | Converted to Day One rich text format |
| `heading` + `html` | `text` | Combined plain text |
| `location` | `location` | Preserved as-is |
| `sun` + `lunar` | `weather` | Parsed for sunrise/sunset and moon phases |
| `tags` | `tags` | Preserved as-is |

## Timezone Handling

The script properly converts Diarium's local time entries to UTC:
- **Input**: Diarium dates in EDT (Eastern Daylight Time)
- **Output**: Day One dates in UTC format
- **Conversion**: Adds 4 hours to convert EDT to UTC

## Troubleshooting

### Common Issues

1. **Date parsing errors**: The script handles various Diarium date formats automatically
2. **Large files**: The script processes entries in batches and shows progress
3. **Import errors**: Ensure the JSON file is named `Journal.json` in the import package

### Error Messages

- `Warning: Media directory not found` - This is normal (media functionality removed)
- `Failed to parse date` - Individual entries with date parsing issues (conversion continues)

## Example

```bash
# Convert your Diarium export
python diarium-to-dayone.py diarium-json/diarium-json.json dayone_import.json

# Create import package for Day One
mkdir dayone_import_package
cp dayone_import.json dayone_import_package/Journal.json
zip -r dayone_import_package.zip dayone_import_package/

# Import into Day One
# 1. Open Day One
# 2. File > Import > Import from ZIP
# 3. Select dayone_import_package.zip
```

## Notes

- **Media files**: Photo/media functionality has been temporarily removed for stability
- **Timezone**: All dates are converted from EDT to UTC for proper Day One import
- **Format**: Uses proper JSON formatting with lowercase booleans for Day One compatibility

## License

This script is provided as-is for converting Diarium exports to Day One format. 