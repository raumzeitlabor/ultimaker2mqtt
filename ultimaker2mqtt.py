import urllib.request
import time
import json
import paho.mqtt.client as mqtt

lastJob = ""
lastState = ""
lastPrinter = ""
client = mqtt.Client()
client.connect_async("mqtt.rzl.so")
client.loop_start()

while True:
    job = '{"state": "none"}'
    printer = '{"status": "unreachable"}'
    try:
        with urllib.request.urlopen("http://ultimaker.rzl.so/api/v1/printer", timeout=10) as response:
            printer = response.read().decode('utf-8')
        with urllib.request.urlopen("http://ultimaker.rzl.so/api/v1/print_job", timeout=10) as response:
            job = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error: {e}")

    state = ""
    try:
        stateJob = json.loads(job)['state']
        statePrinter = json.loads(printer)['status']
        if stateJob == "none":
            state = statePrinter
        else:
            state = stateJob
    except Exception as e:
        state = "error"
        print(f"Error parsing JSON: {e}")

    print(job)
    print(state)

    if state != lastState:
        client.publish("/service/ultimaker/state", payload=state, qos=0, retain=True)
        lastState = state

    if job != lastJob:
        client.publish("/service/ultimaker/job", payload=job, qos=0, retain=True)
        lastJob = job

    if printer != lastPrinter:
        client.publish("/service/ultimaker/printer", payload=printer, qos=0, retain=True)
        lastPrinter = printer

    time.sleep(10)
