# dnsdist – Home Assistant Integration

Custom integration for Home Assistant that connects to the dnsdist API and exposes server statistics and upstream DNS servers as devices with sensors and binary sensors.

## Source project
https://dnsdist.org

---

## Installation

### Installation via HACS

1. Add this repository as a custom repository to HACS:

[![Add Repository](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=metaathron&repository=ha-dnsdist&category=Integration)

2. Use HACS to install the integration.  
3. Restart Home Assistant.  
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dnsdist)

---

### Manual Installation

1. Download the integration files from the GitHub repository.  
2. Place the integration folder in the `custom_components` directory of Home Assistant.  
3. Restart Home Assistant.  
4. Set up the integration using the UI:

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dnsdist)

---

## Setup

1. Go to **Settings → Devices & Services**  
2. Click **Add Integration**  
3. Select **dnsdist**  
4. Enter:
   - API endpoint (e.g. `http://<host>:8083/api/v1/servers/localhost`)
   - API key  

---

## Devices & Entities

### dnsdist Server (main device)

Represents the dnsdist instance.

**Sensors:**
- `dnsdist_uptime`
- `dnsdist_fd_usage`
- `dnsdist_memory_usage`
- `dnsdist_queries`
- `dnsdist_responses`
- `dnsdist_self_answered`
- `dnsdist_cache_hits`
- `dnsdist_cache_misses`

---

### Backend Servers (one device per upstream)

Each upstream server from dnsdist (`servers[]`) is represented as its own device.

**Sensors:**
- `dnsdist_<name>_queries`
- `dnsdist_<name>_responses`
- `dnsdist_<name>_latency`
- `dnsdist_<name>_drop_rate`

**Binary sensor:**
- `dnsdist_<name>_state`

**Attributes (on state entity):**
- `address`
- `protocol`
- `id`
- `name`

**Behavior:**
- Devices are created automatically when a new backend appears
- Devices are removed automatically when a backend disappears

---

## Features

- Server-level monitoring (dnsdist instance)
- Upstream server monitoring as separate devices
- Automatic backend discovery
- Dynamic device creation and removal
- Query and response statistics
- Self-answered queries tracking
- Cache statistics (hits/misses)
- Backend health monitoring (state, latency, drop rate)
- Configurable polling interval

---

## Support

If you find this integration useful, you can support the development:

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/metaathron)

---

## License

This project is licensed under the MIT License.

Copyright (c) 2026 [metaathron](https://github.com/metaathron/)

You are free to use, modify, and distribute this software in accordance with the MIT License.

If you find this project useful, attribution and a link back to the original repository are appreciated:
<https://github.com/metaathron/ha-dnsdist>
