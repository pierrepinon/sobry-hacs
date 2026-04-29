# Sobry — Home Assistant integration

Unofficial integration for [Sobry](https://app.sobry.co), a dynamic electricity provider that prices energy in 15-minute slots.

## Features

- **Current price** — live EUR/kWh price for the ongoing 15-minute slot, refreshed every 15 minutes
- Slot attributes exposed (`color`, `color_label`) for use in automations
- Automatic pre-fetch of next-day prices at 14:00 (Sobry publishes them around 13:30)
- Multi-contract support (e.g. primary + secondary residence)

## Installation via HACS

1. In HACS, go to **Integrations** → ⋮ menu → **Custom repositories**
2. Add `https://github.com/pierrepinon/sobry-hacs` with category **Integration**
3. Search for **Sobry** in HACS and install
4. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & services** → **Add integration**
2. Search for **Sobry**
3. Enter your Sobry email address — an OTP code will be sent to you
4. Enter the code you received

One device is created per contract, each exposing a price sensor.

## Sensor

| Entity | Unit | Description |
|---|---|---|
| `sensor.sobry_<ref>_prix_actuel` | EUR/kWh | Price for the current 15-minute slot |

### Attributes

| Attribute | Example | Description |
|---|---|---|
| `color` | `green` | Tariff tier identifier |
| `color_label` | `Off-peak` | Human-readable tariff tier label |

## Automation example

```yaml
automation:
  - alias: "Start washing machine during cheap slot"
    trigger:
      - platform: state
        entity_id: sensor.sobry_ref_prix_actuel
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.sobry_ref_prix_actuel', 'color') == 'green' }}"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.washing_machine
```

## License

MIT
