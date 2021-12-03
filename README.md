# sensor.sysav
Simple home-assistant sensor for sysav (garbage pickup times)

[![License][license-shield]](LICENSE.md)

## Installation
Install using hacs or manual install

### Manual install
1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `sysav`.
4. Download _all_ the files from the `custom_components/sysav/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

You can try and see what data needs to be entered on https://www.sysav.se/Privat/min-sophamtning/

If you get some results you are satsified with this is the data you need to enter on streetname and streetnumber.

Then add resources after what Kärltyp you want to add a sensor for.

If you are using havs then go to HACS settings and add as a Custom repository.

### Yaml
Full example.
```
  sensor:
    - platform: sysav
      streetname: Trädgårdsvägen       (required)
      streetnumber: 2                  (required)
      resources:
       - "Kärl 1"
       - "Kärl 2"
       - "Trädgårdsavfall"
```

[license-shield]: https://img.shields.io/github/license/custom-components/blueprint.svg?style=for-the-badge

Version:

v1.2.0:
- Added support for Sysavs new endpoint and added city to the request as a required part in the configuration