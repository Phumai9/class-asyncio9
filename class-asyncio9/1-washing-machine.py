import time
import random
import json
import asyncio
import aiomqtt
import os
import sys
from enum import Enum

student_id = "6310301009"


class MachineStatus(Enum):
    pressure = round(random.uniform(2000, 3000), 2)
    temperature = round(random.uniform(25.0, 40.0), 2)
    #
    # add more machine status
    #


class MachineMaintStatus(Enum):
    filter = random.choice(["clear", "clogged"])
    noise = random.choice(["quiet", "noisy"])
    #
    # add more maintenance status
    #


class WashingMachine:
    def __init__(self, serial):
        self.MACHINE_STATUS = 'OFF'
        self.SERIAL = serial


async def publish_message(w, client, app, action, name, value):
    print(f"{time.ctime()} - [{w.SERIAL}] {name}:{value}")
    await asyncio.sleep(2)
    payload = {
        "action": "get",
        "project": student_id,
        "model": "model-01",
        "serial": w.SERIAL,
        "name": name,
        "value": value
    }
    print(
        f"{time.ctime()} - PUBLISH - [{w.SERIAL}] - {payload['name']} > {payload['value']}")
    await client.publish(f"v1cdti/{app}/{action}/{student_id}/model-01/{w.SERIAL}", payload=json.dumps(payload))


async def CoroWashingMachine(w, client):
    # washing coroutine
    while True:
        wait_next = round(10*random.random(), 2)
        print(
            f"{time.ctime()} - [{w.SERIAL}] Waiting to start... {wait_next} seconds.")
        await asyncio.sleep(wait_next)
        if w.MACHINE_STATUS == 'OFF':
            continue
        if w.MACHINE_STATUS == 'ON':

            await publish_message(w, client, "app", "get", "STATUS", "START")

            await publish_message(w, client, "app", "get", "LID", "OPEN")

            await publish_message(w, client, "app", "get", "STATUS", "CLOSE")

 # random status
            status = random.choice(list(MachineStatus))
            await publish_message(w, client, "app", "get", status.name, status.value)

            await publish_message(w, client, "app", "get",  "STATUS", "FINISHED")

# random maintance
            maint = random.choice(list(MachineMaintStatus))
            await publish_message(w, client, "app", "get", maint.name, maint.value)
            if (maint.name == 'noise' and maint.value == 'noisy'):
                w.MACHINE_STATUS = 'OFF'

            await publish_message(w, client, "app", "get",  "STATUS", "STOPPED")

            await publish_message(w, client, "app", "get",  "STATUS", "POWER OFF")
            w.MACHINE_STATUS = 'OFF'


async def listen(w, client):
    async with client.messages() as messages:
        await client.subscribe(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}")
        async for message in messages:
            m_decode = json.loads(message.payload)
            if message.topic.matches(f"v1cdti/hw/set/{student_id}/model-01/{w.SERIAL}"):
                # set washing machine status
                print(
                    f"{time.ctime} -- MQTT -- [{m_decode['serial']}]:{m_decode['name']} => {m_decode['value']})")
                w.MACHINE_STATUS = 'ON'


async def main():
    w = WashingMachine(serial='SN-001')
    async with aiomqtt.Client("test.mosquitto.org") as client:
        await asyncio.gather(listen(w, client), CoroWashingMachine(w, client))

# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

asyncio.run(main())

# Wed Aug 30 15:06:40 2023 - [SN-001] Waiting to start... 8.58 seconds.
# <built-in function ctime> -- MQTT -- [SN-001]:POWER => ON)
# Wed Aug 30 15:06:48 2023 - [SN-001] STATUS:START
# Wed Aug 30 15:06:50 2023 - PUBLISH - [SN-001] - STATUS > START
# Wed Aug 30 15:06:50 2023 - [SN-001] LID:OPEN
# Wed Aug 30 15:06:52 2023 - PUBLISH - [SN-001] - LID > OPEN
# Wed Aug 30 15:06:52 2023 - [SN-001] STATUS:CLOSE
# Wed Aug 30 15:06:54 2023 - PUBLISH - [SN-001] - STATUS > CLOSE
# Wed Aug 30 15:06:54 2023 - [SN-001] pressure:2309.27
# Wed Aug 30 15:06:56 2023 - PUBLISH - [SN-001] - pressure > 2309.27
# Wed Aug 30 15:06:56 2023 - [SN-001] STATUS:FINISHED
# Wed Aug 30 15:06:58 2023 - PUBLISH - [SN-001] - STATUS > FINISHED
# Wed Aug 30 15:06:58 2023 - [SN-001] filter:clogged
# Wed Aug 30 15:07:00 2023 - PUBLISH - [SN-001] - filter > clogged
# Wed Aug 30 15:07:00 2023 - [SN-001] STATUS:STOPPED
# Wed Aug 30 15:07:02 2023 - PUBLISH - [SN-001] - STATUS > STOPPED
# Wed Aug 30 15:07:02 2023 - [SN-001] STATUS:POWER OFF
# Wed Aug 30 15:07:04 2023 - PUBLISH - [SN-001] - STATUS > POWER OFF
# Wed Aug 30 15:07:04 2023 - [SN-001] Waiting to start... 7.06 seconds.
# Wed Aug 30 15:07:11 2023 - [SN-001] Waiting to start... 3.1 seconds.
# Wed Aug 30 15:07:14 2023 - [SN-001] Waiting to start... 3.59 seconds.
# Wed Aug 30 15:07:18 2023 - [SN-001] Waiting to start... 9.02 seconds.
# <built-in function ctime> -- MQTT -- [SN-001]:POWER => ON)
# Wed Aug 30 15:07:27 2023 - [SN-001] STATUS:START
# Wed Aug 30 15:07:29 2023 - PUBLISH - [SN-001] - STATUS > START
# Wed Aug 30 15:07:29 2023 - [SN-001] LID:OPEN
# Wed Aug 30 15:07:31 2023 - PUBLISH - [SN-001] - LID > OPEN
# Wed Aug 30 15:07:31 2023 - [SN-001] STATUS:CLOSE
# Wed Aug 30 15:07:33 2023 - PUBLISH - [SN-001] - STATUS > CLOSE
# Wed Aug 30 15:07:33 2023 - [SN-001] temperature:28.35
# Wed Aug 30 15:07:35 2023 - PUBLISH - [SN-001] - temperature > 28.35
# Wed Aug 30 15:07:35 2023 - [SN-001] STATUS:FINISHED
# Wed Aug 30 15:07:37 2023 - PUBLISH - [SN-001] - STATUS > FINISHED
# Wed Aug 30 15:07:37 2023 - [SN-001] noise:quiet
# Wed Aug 30 15:07:39 2023 - PUBLISH - [SN-001] - noise > quiet
# Wed Aug 30 15:07:39 2023 - [SN-001] STATUS:STOPPED
# Wed Aug 30 15:07:41 2023 - PUBLISH - [SN-001] - STATUS > STOPPED
# Wed Aug 30 15:07:41 2023 - [SN-001] STATUS:POWER OFF
# Wed Aug 30 15:07:43 2023 - PUBLISH - [SN-001] - STATUS > POWER OFF
# Wed Aug 30 15:07:43 2023 - [SN-001] Waiting to start... 8.62 seconds.
# Wed Aug 30 15:07:52 2023 - [SN-001] Waiting to start... 2.86 seconds.
# Wed Aug 30 15:07:54 2023 - [SN-001] Waiting to start... 9.6 seconds.
# Wed Aug 30 15:08:04 2023 - [SN-001] Waiting to start... 6.85 seconds.
# Wed Aug 30 15:08:11 2023 - [SN-001] Waiting to start... 1.65 seconds.
# Wed Aug 30 15:08:13 2023 - [SN-001] Waiting to start... 8.2 seconds.
# Wed Aug 30 15:08:21 2023 - [SN-001] Waiting to start... 1.27 seconds.
# Wed Aug 30 15:08:22 2023 - [SN-001] Waiting to start... 4.04 seconds.