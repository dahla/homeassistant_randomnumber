# Random Number Sensor for Home Assistant

This integration allows you to create multiple virtual sensors that generate random values at a specific interval.

## Local Installation
1.  Access your Home Assistant files (via Samba, SSH, or VS Code add-on).
2.  Navigate to your `config` directory.
3.  If it doesn't exist, create a folder named `custom_components`.
4.  Create a folder named `random_sensor` inside `custom_components`.
5.  Copy all the files from this repository into that folder.
6.  **Restart Home Assistant.**
7.  In the HA UI, go to **Settings** -> **Devices & Services**.
8.  Click **Add Integration** and search for "Random Number Generator".

## Configuration
When adding the integration, you can configure:
- **Name**: The name of the sensor.
- **Minimum Value**: The lowest possible random number.
- **Maximum Value**: The highest possible random number.
- **Interval**: How often (in seconds) the value should update.

## How to Publish
To share this with the community, the best way is via **HACS (Home Assistant Community Store)**.

### 1. Prepare GitHub Repository
- Create a new public repository on GitHub.
- Push your `custom_components/random_sensor/` files to the repo. 
- Ensure your structure looks like this in the repo:


### 2. Add to HACS (For personal use/testing)
- Open HACS in your Home Assistant.
- Click the three dots (top right) and select **Custom repositories**.
- Paste your GitHub URL and select **Integration** as the category.

### 3. Share with Everyone
- To make it searchable for everyone in HACS, you must submit a Pull Request to the [HACS Default Repository](https://github.com/hacs/default).
- Ensure you have a valid `manifest.json` and a `hacs.json` file (optional but recommended for HACS features).