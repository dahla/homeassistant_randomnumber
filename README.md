# Random Sensor with History Backfill

A Home Assistant integration that creates sensors which generate random numbers at specified intervals and pre-populates historical data upon setup.

## Features
- **Configurable Range**: Set Min and Max values per sensor.
- **Configurable Interval**: Choose how often the value changes.
- **Historical Backfill**: Generates past data points so your graphs aren't empty when you first install it.

## Installation via HACS (Recommended)
1. Open **HACS** in Home Assistant.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add the URL of this repository and select **Integration** as the category.
4. Click **Install**.
5. **Restart** Home Assistant.

## Manual Installation
1. Copy the `custom_components/random_sensor` directory into your HA `config/custom_components` directory.
2. Restart Home Assistant.

## Setup
1. Go to **Settings > Devices & Services**.
2. Click **Add Integration**.
3. Search for **Random Number Generator**.
4. Follow the configuration steps:
   - **Name**: "My Random Sensor"
   - **Min**: 0
   - **Max**: 100
   - **Interval**: 60 (updates every minute)
   - **Historic Items**: 50 (will create 50 points of data starting from 50 minutes ago)

## Development
To update the integration:
1. Push changes to GitHub.
2. Create a new GitHub Release.
3. HACS will automatically detect the update.