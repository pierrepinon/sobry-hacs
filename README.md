# Sobry — Home Assistant integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![Project Stage][project-stage-shield]][project-stage]

_Component to integrate [Sobry](https://app.sobry.co) with [Home Assistant][homeassistant]._

Sobry is a dynamic electricity provider in France that prices energy in 15-minute slots, allowing you to optimize your consumption based on real-time prices.

## ✨ Features

- **💰 Current price** — Live EUR/kWh price for the ongoing 15-minute slot, refreshed every 15 minutes
- **🎨 Tariff tiers** — Slot attributes exposed (`color`, `color_label`) for use in automations
- **📅 Next-day prices** — Automatic pre-fetch of next-day prices at 14:00 (Sobry publishes them around 13:30)
- **🏠 Multi-contract support** — Manage multiple contracts (e.g., primary + secondary residence)
- **📊 Consumption tracking** — Monthly energy consumption and cost sensors
- **⚡ Power monitoring** — Subscribed power diagnostic sensor

## 📥 Installation

### Via HACS (Recommended)

1. In HACS, go to **Integrations** → ⋮ menu → **Custom repositories**
2. Add `https://github.com/pierrepinon/sobry-hacs` with category **Integration**
3. Search for **Sobry** in HACS and install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/sobry` directory to your Home Assistant configuration directory
2. Restart Home Assistant

## ⚙️ Configuration

1. Go to **Settings** → **Devices & services** → **Add integration**
2. Search for **Sobry**
3. Enter your Sobry email address — an OTP code will be sent to you
4. Enter the code you received

One device is created per contract, each exposing multiple sensors.

## 📡 Entities

### Sensors

Each contract creates the following sensors:

| Entity | Unit | Description | Device Class | State Class |
|---|---|---|---|---|
| `sensor.sobry_<ref>_current_price` | EUR/kWh | Price for the current 15-minute slot | - | - |
| `sensor.sobry_<ref>_monthly_energy` | kWh | Monthly energy consumption | Energy | Total |
| `sensor.sobry_<ref>_monthly_price` | EUR | Monthly electricity cost | Monetary | - |
| `sensor.sobry_<ref>_subscribed_power` | kVA | Contracted maximum power | - | - |

### Current Price Sensor Attributes

| Attribute | Example | Description |
|---|---|---|
| `color` | `green` | Tariff tier identifier (green, yellow, red, etc.) |
| `color_label` | `Off-peak` | Human-readable tariff tier label |

## 🤖 Automation Examples

### Start appliances during cheap slots

```yaml
automation:
  - alias: "Start washing machine during off-peak hours"
    trigger:
      - platform: state
        entity_id: sensor.sobry_ref_current_price
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.sobry_ref_current_price', 'color') == 'green' }}"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.washing_machine
```

### Notify when price changes to peak

```yaml
automation:
  - alias: "Notify when price enters peak hours"
    trigger:
      - platform: state
        entity_id: sensor.sobry_ref_current_price
        attribute: color
        to: red
    action:
      - service: notify.notify
        data:
          title: "⚡ Peak electricity price"
          message: "Electricity price is now at peak rate ({{ states('sensor.sobry_ref_current_price') }} EUR/kWh)"
```

### Delay high-power devices until off-peak

```yaml
automation:
  - alias: "Delay oven until off-peak"
    trigger:
      - platform: state
        entity_id: switch.oven
        to: "on"
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.sobry_ref_current_price', 'color') != 'green' }}"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.oven
      - delay: "00:30:00"  # Wait 30 minutes
      - service: switch.turn_on
        target:
          entity_id: switch.oven
```

### Track daily electricity cost

```yaml
sensor:
  - platform: template
    sensors:
      daily_electricity_cost:
        friendly_name: "Daily Electricity Cost"
        unit_of_measurement: "EUR"
        value_template: >
          {% set price = states('sensor.sobry_ref_current_price') | float %}
          {% set energy = states('sensor.total_daily_energy') | float %}
          {{ (price * energy) | round(2) }}
```

## 🛠️ Troubleshooting

### Connection Issues

**Symptom:** Sensors show "unavailable" or "unknown"

**Solutions:**
1. Check your internet connection
2. Verify your Sobry credentials are correct
3. Restart Home Assistant
4. Check the logs for error messages:
   - Go to **Settings** → **System** → **Logs**
   - Filter for `sobry` or `error`

### OTP Code Not Received

**Symptom:** No OTP code received during setup

**Solutions:**
1. Check your spam folder
2. Wait a few minutes and try again
3. Verify your email address is correct
4. Ensure your Sobry account is active

### Prices Not Updating

**Symptom:** Price sensors show old values

**Solutions:**
1. Wait up to 15 minutes for the next update cycle
2. Check if Sobry has published prices for the current day
3. Restart Home Assistant to force a refresh
4. Verify your token hasn't expired (re-authenticate if needed)

### Common Error Messages

| Error | Meaning | Solution |
|---|---|---|
| `cannot_connect` | Cannot reach Sobry API | Check internet connection |
| `invalid_auth` | Invalid OTP code | Request a new code and try again |
| `unauthorized` | Invalid or expired token | Re-authenticate in integration settings |

## 📊 Data Privacy

This integration:
- ✅ Only accesses your Sobry account data
- ✅ Does not store your data externally
- ✅ Uses OAuth2 with short-lived tokens
- ✅ All communication is encrypted (HTTPS)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/pierrepinon/sobry-hacs.svg?style=for-the-badge
[commits]: https://github.com/pierrepinon/sobry-hacs/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/pierrepinon/sobry-hacs.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Pierre%20Pinon-blue.svg?style=for-the-badge
[project-stage]: https://github.com/pierrepinon/sobry-hacs
[project-stage-shield]: https://img.shields.io/badge/project-stage-production-green.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/pierrepinon/sobry-hacs.svg?style=for-the-badge
[releases]: https://github.com/pierrepinon/sobry-hacs/releases
[user_profile]: https://github.com/pierrepinon
[homeassistant]: https://www.home-assistant.io/
