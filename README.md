# FrankenBean
<p align="center">
	<img alt="GitHub language count" src="https://img.shields.io/github/languages/count/the-amaya/FrankenBean?style=plastic">
	<img alt="GitHub top language" src="https://img.shields.io/github/languages/top/the-amaya/FrankenBean?style=plastic">
	<img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/the-amaya/FrankenBean?style=plastic">
	<img alt="GitHub" src="https://img.shields.io/github/license/the-amaya/FrankenBean?style=plastic">
	<img alt="GitHub contributors" src="https://img.shields.io/github/contributors/the-amaya/FrankenBean?style=plastic">
	<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/the-amaya/FrankenBean?style=plastic">
</p>
The ultimate coffee pot

This project is for the control of the FrankenBean Coffee maker


# API endpoint documentation and usage examples.

## Overview
```json
{
  "key": "<int>",
  "name": "<name of the thing>",
  "state": "<the current value of the thing>"
}
```

### get all IO devices and their states
**all sensors and output**

`GET /state/all`

***Response example***

- `202 OK` on success

```json
[
  {
    "id": 1,
    "name": "pump",
    "state": 0
  },
  {
    "id": 2,
    "name": "w_solenoid",
    "state": 0
  },
  {
    "id": 3,
    "name": "heat",
    "state": 0
  },
  {
    "id": 4,
    "name": "vent",
    "state": 0
  },
  {
    "id": 5,
    "name": "air_pump",
    "state": 0
  },
  {
    "id": 6,
    "name": "fill_low",
    "state": 0
  },
  {
    "id": 7,
    "name": "fill_med",
    "state": 0
  },
  {
    "id": 8,
    "name": "fill_high",
    "state": 0
  },
  {
    "id": 9,
    "name": "overfill",
    "state": 0
  },
  {
    "id": 10,
    "name": "flow",
    "state": 0
  },
  {
    "id": 11,
    "name": "temperature",
    "state": 0
  },
  {
    "id": 12,
    "name": "active",
    "state": 0
  },
  {
    "id": 13,
    "name": "start_time",
    "state": 0
  },
  {
    "id": 14,
    "name": "current_time",
    "state": 0
  },
  {
    "id": 15,
    "name": "end_time",
    "state": 0
  }
]
```



**single sensor or output**

`GET /state/<name>`
- for available <name>s see the detailed list at the end of this document)

***Response example***
`GET /state/pump`
- `202 OK` on success

```json
{
  "id": 1,
  "name": "pump",
  "state": 0
}
```

**list of endpoints**
`GET /state/all`
- returns full state table

`GET /state/pump`
- pump state (on or off as 1 or 0, respectfully)

`GET /state/w_solenoid`
- water in solenoid state (on or off as 1 or 0, respectfully)

`GET /state/heat`
- heater state (on or off as 1 or 0, respectfully)

`GET /state/vent`
- air vent state (on or off as 1 or 0, respectfully)

`GET /state/air_pump`
- air pump state (on or off as 1 or 0, respectfully)

`GET /state/fill_low`
- fill level (0 if water level below this level, 1 if water level at or above)

`GET /state/fill_med`
- fill level (0 if water level below this level, 1 if water level at or above)

`GET /state/fill_high`
- fill level (0 if water level below this level, 1 if water level at or above)

`GET /state/overfill`
- fill level (0 if water level below this level, 1 if water level at or above)

`GET /state/flow`
- count from the flow sensor (not currently used, may not be reliable)

`GET /state/temperature`
- raw value of the thermister. ~50ish is around room temp, ~950ish is good for brewing coffee

`GET /state/active`
- returns 0 when when idle, returns 1 (along with a 503 error) if there is already a brew in progress

`GET /state/start_time`
- time the current brew was started (not sure what format I will use for dates, if you have a preference let me know)

`GET /state/current_time`
- current time on the server (not sure what format I will use for dates, if you have a preference let me know)

`GET /state/end_time`
- time the most recent brew completed (not sure what format I will use for dates, if you have a preference let me know)
- note: this is not persistant on program restarts.

`POST /command/brew`
- start a brew cycle (returns a 202 on success, and a 503 on failure)