#!/usr/bin/env python3
"""
Convert a Diarium JSON export to Day One JSON format with media support.
Usage:
    python diarium_to_dayone.py diarium.json dayone_import.json
"""

import json
import uuid
import sys
import datetime as dt
import os
import shutil
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup
import re

def html_to_richtext(html: str) -> str:
    """Convert HTML to Day One rich text format."""
    if not html:
        return ""
    
    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")
    
    # Convert to rich text format
    contents = []
    line_id = str(uuid.uuid4()).upper()
    
    # Extract text and preserve basic formatting
    text = soup.get_text("\n").strip()
    
    # Create rich text structure
    rich_text = {
        "contents": [
            {
                "attributes": {
                    "line": {
                        "header": 0,
                        "identifier": line_id
                    }
                },
                "text": text
            }
        ],
        "meta": {
            "created": {
                "platform": "com.bloombuilt.dayone-mac",
                "version": 1667
            },
            "small-lines-removed": True,
            "version": 1
        }
    }
    
    return json.dumps(rich_text, ensure_ascii=False)

def parse_weather_data(sun: str, lunar: str) -> dict:
    """Parse weather data from Diarium format to Day One format."""
    weather = {
        "weatherCode": "clear",
        "weatherServiceName": "WeatherKit",
        "temperatureCelsius": 20.0,
        "windBearing": 0,
        "conditionsDescription": "Clear",
        "pressureMB": 1013.0,
        "visibilityKM": 10.0,
        "relativeHumidity": 50,
        "windSpeedKPH": 0.0
    }
    
    # Parse sunrise/sunset from sun string
    if sun and "Sunrise:" in sun and "Sunset:" in sun:
        try:
            # Extract times from format like "☀️ Sunrise: 7:16 AM Sunset: 7:56 PM"
            sun_match = re.search(r"Sunrise: (\d+):(\d+)\s*(AM|PM).*Sunset: (\d+):(\d+)\s*(AM|PM)", sun)
            if sun_match:
                sunrise_hour = int(sun_match.group(1))
                sunrise_minute = int(sun_match.group(2))
                sunrise_ampm = sun_match.group(3)
                sunset_hour = int(sun_match.group(4))
                sunset_minute = int(sun_match.group(5))
                sunset_ampm = sun_match.group(6)
                
                # Convert to 24-hour format
                if sunrise_ampm == "PM" and sunrise_hour != 12:
                    sunrise_hour += 12
                elif sunrise_ampm == "AM" and sunrise_hour == 12:
                    sunrise_hour = 0
                    
                if sunset_ampm == "PM" and sunset_hour != 12:
                    sunset_hour += 12
                elif sunset_ampm == "AM" and sunset_hour == 12:
                    sunset_hour = 0
                
                # Create sunrise/sunset dates (using current date as base)
                today = dt.datetime.now()
                sunrise_date = today.replace(hour=sunrise_hour, minute=sunrise_minute, second=0, microsecond=0)
                sunset_date = today.replace(hour=sunset_hour, minute=sunset_minute, second=0, microsecond=0)
                
                weather["sunriseDate"] = sunrise_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                weather["sunsetDate"] = sunset_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        except:
            pass
    
    # Parse moon phase from lunar string
    if lunar:
        if "Waxing gibbous" in lunar:
            weather["moonPhaseCode"] = "waxing-gibbous"
            weather["moonPhase"] = 0.75
        elif "Waning gibbous" in lunar:
            weather["moonPhaseCode"] = "waning-gibbous"
            weather["moonPhase"] = 0.25
        elif "Third quarter" in lunar:
            weather["moonPhaseCode"] = "third-quarter"
            weather["moonPhase"] = 0.5
        elif "New moon" in lunar:
            weather["moonPhaseCode"] = "new-moon"
            weather["moonPhase"] = 0.0
        elif "Full moon" in lunar:
            weather["moonPhaseCode"] = "full-moon"
            weather["moonPhase"] = 1.0
        else:
            weather["moonPhaseCode"] = "waxing-gibbous"
            weather["moonPhase"] = 0.37
    
    return weather

def find_media_files(entry_date: str, media_dir: Path) -> list:
    """Find media files associated with an entry date."""
    media_files = []
    # Robust date parsing (handles microseconds or not)
    try:
        entry_dt = dt.datetime.fromisoformat(entry_date)
    except ValueError:
        if "." in entry_date:
            base, frac = entry_date.split(".", 1)
            frac = (frac + "000000")[:6]
            entry_date_fixed = f"{base}.{frac}"
            entry_dt = dt.datetime.fromisoformat(entry_date_fixed)
        else:
            raise
    # Try different date formats that might match media folders
    possible_formats = [
        entry_dt.strftime("%Y-%m-%d"),
        entry_dt.strftime("%Y-%m-%d_%H%M%S%f")[:-3],  # Remove microseconds
        entry_dt.strftime("%Y-%m-%d_%H%M%S"),
        entry_dt.strftime("%Y%m%d"),
        entry_dt.strftime("%Y%m%d_%H%M%S")
    ]
    for date_format in possible_formats:
        for folder in media_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(date_format):
                for file_path in folder.rglob("*"):
                    if file_path.is_file():
                        media_files.append(str(file_path))
    return media_files

def build_entry(d, media_dir: Optional[Path] = None):
    """Build a Day One entry from Diarium data."""
    # 1) date → creationDate (UTC "Z")
    date_str = d["date"]
    try:
        ts = dt.datetime.fromisoformat(date_str)
    except ValueError:
        # Try to trim microseconds if present (e.g. '2010-10-26T15:47:53.48828')
        if "." in date_str:
            base, frac = date_str.split(".", 1)
            # Pad/truncate to 6 digits for microseconds
            frac = (frac + "000000")[:6]
            date_str_fixed = f"{base}.{frac}"
            ts = dt.datetime.fromisoformat(date_str_fixed)
        else:
            raise
    creation = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 2) main body
    body = BeautifulSoup(d.get("html", ""), "html.parser").get_text("\n").strip()
    if d.get("heading"):
        body = f"{d['heading']}\n\n{body}"
    
    # 3) rich text
    rich_text = html_to_richtext(d.get("html", ""))
    
    # 4) weather data
    weather = parse_weather_data(d.get("sun", ""), d.get("lunar", ""))
    
    # 5) location
    location = None
    if d.get("location"):
        lat, lon = d["location"]
        location = {
            "region": {
                "center": {
                    "longitude": lon,
                    "latitude": lat
                },
                "radius": 75
            },
            "localityName": "Unknown",
            "country": "United States",
            "timeZoneName": "America/New_York",
            "administrativeArea": "OH",
            "longitude": lon,
            "placeName": "Unknown",
            "latitude": lat
        }
    
    # 6) media files
    media_files = []
    if media_dir:
        media_files = find_media_files(d["date"], media_dir)
    
    entry = {
        "creationDate": creation,
        "creationOSVersion": "15.5",
        "isAllDay": False,
        "creationDevice": "Diarium Import",
        "duration": 0,
        "weather": weather,
        "isPinned": False,
        "timeZone": "America/New_York",
        "starred": False,
        "creationDeviceType": "Unknown",
        "richText": rich_text,
        "modifiedDate": creation,
        "text": body,
        "editingTime": 0
    }
    
    if location:
        entry["location"] = location
    
    if d.get("tags"):
        entry["tags"] = d["tags"]
    
    # Add media references if we have media files
    if media_files:
        entry["media"] = []
        for i, media_path in enumerate(media_files):
            entry["media"].append({
                "identifier": str(uuid.uuid4()).upper().replace("-", ""),
                "type": "image",  # Assume images for now
                "filename": f"media_{i:04d}{Path(media_path).suffix}"
            })
    
    return entry

def convert_diarium_to_dayone(src, dest):
    """Convert Diarium JSON to Day One JSON format."""
    print(f"Reading Diarium data from {src}...")
    diarium_data = json.loads(Path(src).read_text(encoding="utf-8"))
    
    # Check if media directory exists
    media_dir = Path("diarium-json/media")
    if not media_dir.exists():
        print("Warning: Media directory not found, proceeding without media files.")
        media_dir = None
    
    print(f"Converting {len(diarium_data)} entries...")
    
    # Convert entries
    entries = []
    for i, entry in enumerate(diarium_data):
        if i % 100 == 0:
            print(f"Processing entry {i+1}/{len(diarium_data)}...")
        
        dayone_entry = build_entry(entry, media_dir)
        entries.append(dayone_entry)
    
    # Create output structure
    journal_data = {
        "metadata": {
            "version": "1.0"
        },
        "entries": entries
    }
    
    # Write JSON file
    print(f"Writing {len(entries)} entries to {dest}...")
    Path(dest).write_text(json.dumps(journal_data, ensure_ascii=False, indent=2))
    
    print(f"Successfully converted {len(entries)} entries → {dest}")
    
    # Report media files found
    if media_dir and media_dir.exists():
        total_media_files = sum(1 for f in media_dir.rglob("*") if f.is_file())
        print(f"Found {total_media_files} media files in {media_dir}")
    
    return dest

def main(src, dest):
    """Main conversion function."""
    convert_diarium_to_dayone(src, dest)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python diarium_to_dayone.py <diarium.json> <output.json>")
        print("Example: python diarium_to_dayone.py diarium-json/diarium-json.json dayone_import.json")
        print("\nThis will create a Day One JSON file that you can manually zip for import.")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2])