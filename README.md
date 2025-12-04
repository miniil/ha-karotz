# Karotz Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Custom integration to control your Karotz rabbit from Home Assistant.

## Features

- **Status sensor**: Monitor your Karotz connectivity
- **LED control**: RGB light with colors, pulse effects
- **TTS service**: Make your rabbit speak
- **Wake/Sleep switches**: Control rabbit state

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots menu → "Custom repositories"
4. Add this repository URL and select "Integration"
5. Search for "Karotz" and install
6. Restart Home Assistant

### Manual

1. Copy `custom_components/karotz` to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Karotz"
3. Enter your Karotz IP address

## Services

### karotz.say

Make your Karotz speak.

```yaml
service: karotz.say
data:
  text: "Hello from Home Assistant!"
  voice: 2
```

## Automation Example

```yaml
automation:
  - alias: "Door open announcement"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: karotz.say
        data:
          text: "The front door is open"
```

## Requirements

- Karotz with OpenKarotz firmware
- Network connectivity between Home Assistant and Karotz

## Support

If you encounter issues, please [open an issue](https://github.com/miniil/ha-karotz/issues) on GitHub.

## License

MIT License - see [LICENSE](LICENSE) file.