import subprocess
import time
import os
import csv
import sys

"""
parametros:

1. Archivo de mundos
2. Repeticiones por mundos
3. Nombre de archivo csv

"""

logDirectory = "./Erebus-v21_2_2/game/logs/"

configFile = sys.argv[1]
csvFileName = sys.argv[2]

with open(configFile, "r") as config:
    for line in config.readlines():
        line = line.replace("\n", "")
        name, argument = line.split("=")
        print(name, "=", argument)
        if name == "controller":
            controller = argument
        elif name == "worlds":
            worldsFile = argument
        elif name == "reps":
            repetitionsPerWorld = int(argument)


def loadController(controller):
    erebusControllerPath = "./Erebus-v21_2_2/game/controllers/robot0Controller/robot0Controller.py"

    with open(controller, "r") as contToLoad:
        with open(erebusControllerPath, "w") as contToWrite:
            contToWrite.write(contToLoad.read())
    
    print(f"Loaded {controller}")

def openWebots(world):
    script = f"""#!/bin/bash
    xvfb-run webots --stderr --batch --mode=fast --no-rendering --no-sandbox {world}
    """

    minimize = """#!/bin/bash
    xdotool windowminimize $(xdotool getactivewindow)
    """
    rc = subprocess.Popen(script, shell=True)

    time.sleep(1)

    #subprocess.Popen(minimize, shell=True)

def killWebots():
    script = """#!/bin/bash
    pkill webots
    """
    rc = subprocess.Popen(script, shell=True)

def processLogs(world, fileName):
    lastLog = sorted(os.listdir(logDirectory))[-1]

    if "gameLog" in lastLog:
        with open(logDirectory + lastLog, "r") as log:
            lines = log.readlines()
        
        finalLine = lines[-1]
        finalTime = (int(finalLine[0:2]) * 60) + int(finalLine[3:5])
        print("Final time:", finalTime)

        for line in lines:
            if "ROBOT_0_SCORE: " in line:
                line = line.replace("ROBOT_0_SCORE: ", "")
                line = line.replace("\n", "")
                finalScore = float(line)
                print("Final score:", finalScore)
        
        with open("./" + fileName, "a") as file:
            writer = csv.writer(file)

            writer.writerow([world.split("/")[-1], finalScore, finalTime])

def testRun(world, fileName):
    initialLogNumber = len(os.listdir(logDirectory))
    newLogNumber = len(os.listdir(logDirectory))

    print("Opening webots with world:", world)
    openWebots(world)
    while initialLogNumber == newLogNumber:
        newLogNumber = len(os.listdir(logDirectory))

    time.sleep(1)

    print("Closing webots...")
    killWebots()

    print("Processing data...")
    processLogs(world, fileName)


with open("./" + csvFileName, "w") as file:
    writer = csv.writer(file)
    writer.writerow(["World", "Score", "Time"])

loadController(controller)

with open(worldsFile, "r") as worlds:
    lines = worlds.readlines()

    actualRuns = 0
    totalRuns = len(lines) * int(repetitionsPerWorld)

    for world in lines:
        world = world.replace("\n", "")
        for i in range(int(repetitionsPerWorld)):
            testRun(world, csvFileName)
            actualRuns += 1
            time.sleep(1)
            print("Tested", actualRuns, "/", totalRuns, "simulations")





