#!/usr/bin/env python3

import requests
import socket
import time
import os
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=env_path)

from datetime import datetime

# Shelly
SHELLY_URL = os.getenv("SHELLY_URL", "http://192.168.0.132/rpc/Shelly.GetStatus")

# New Relic
NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY")
NEW_RELIC_EVENT_API = os.getenv("NEW_RELIC_EVENT_API", "https://insights-collector.newrelic.com/v1/accounts/events")

HOSTNAME = socket.gethostname()

try:
    # Obtener métricas del Shelly
    response = requests.get(SHELLY_URL, timeout=10)
    response.raise_for_status()

    data = response.json()

    switch = data.get("switch:0", {})
    energy = switch.get("aenergy", {})

    event = {
        "eventType": "metricsConsumptionPc",
        "hostname": HOSTNAME,
        "deviceName": "Shelly-PC",

        "switchId": switch.get("id"),
        "output": switch.get("output"),

        "apower": switch.get("apower"),
        "voltage": switch.get("voltage"),
        "frequency": switch.get("freq"),
        "current": switch.get("current"),

        "energyTotal": energy.get("total"),
        "energyMinute0": energy.get("by_minute", [None, None, None])[0],
        "energyMinute1": energy.get("by_minute", [None, None, None])[1],
        "energyMinute2": energy.get("by_minute", [None, None, None])[2],
        "energyMinuteTs": energy.get("minute_ts")
    }

    headers = {
        "Api-Key": NEW_RELIC_LICENSE_KEY,
        "Content-Type": "application/json"
    }

    nr_response = requests.post(
        NEW_RELIC_EVENT_API,
        headers=headers,
        json=[event],
        timeout=10
    )

    nr_response.raise_for_status()

    print(f"[{datetime.now()}] Evento enviado correctamente")
#    print(event)

except Exception as e:
    print(f"ERROR: {e}")
