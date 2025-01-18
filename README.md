# Battery-Notifications

Automating a laptop task that gets notifications when the battery reaches a determined level

## Introduction

By making improper use of my laptop's battery charge, I have caused significant deterioration to the point that the battery is now in a severely damaged state.

Even though this component can be replaced with a new one, I found that my laptop, **which runs on Windows 11**, has a way of notifying the user when the battery is running low. However, it does not have a way to notify the user when the battery is about to reach 100%, which is the case that has caused the deterioration of my battery.

This is why I decided to automate this process with a Python script and be alerted to plug or unplug the device when the battery approaches very low or very high levels, respectively and to develop the solution together with my brother [PPolux21](https://github.com/PPolux21), working side by side to automate this task.

The goal of this development was to detect if the computer's battery reached a minimum limit to plug it in, or a maximum limit to unplug it, and notify the user through a desktop and audible notification on the computer, as well as a notification to the user's phone implemented through a service. Some alternatives considered and discarded included WhatsApp, Discord, e-mail, or SMS.

## The Process, Setup and Usage

- Python was used to carry out the automation task.
- The ```psutil``` library was used to check the battery level and whether it was charging or not.
- The ```notify-py``` library was used to send notification messages to the computer.
- The ```requests``` library was used to make a request through the Telegram API to a custom bot that would send another notification to our chats.
- The ```playsound``` library was used to play a sound as part of the computer's notification.
- The ```signal``` library was used to check signals sent to the system and recognize the end of the program's execution, allowing a notification to be sent at that point.
- The ```dotenv``` library was used to store sensitive information in a file external to the developed code.
- The ```argparse``` library was used to support console arguments and make the automation of this task more customizable.
- Telegram and its API, as well as its bot development extension, were used in the objective section to send this notification to the user's phone.

For personal use, it is required to create a .env file in the root of this repository with the following structure:

```
TOKEN=""
CHAT_ID=""
```

Where:

- ```TOKEN``` is the token of the created Telegram bot
- ```CHAT_ID``` is the personal chat ID to which the notification will be sent.

In a folder called ```sounds```, there are the sound files that will be played as part of the corresponding notification, and the selection of the authors of these sounds is not included in this repository.

After this setup, the program can be used through the console with a command like the following:

```bash
python BatteryChecker.py
```

If nothing is specified, some parameters for configuring the task will take their default values. These customizable parameters are:

- ```--lower```: Specifies the minimum acceptable battery level, in a range from 0 to 100. If the battery level drops below this value, notifications will start being sent every 90 seconds (default value is 20).
- ```--higher```: Specifies the maximum acceptable battery level, in a range from 0 to 100. If the battery keeps charging beyond this value, notifications will start being sent every 90 seconds (default value is 90).
- ```--sound```: A boolean value indicating whether or not sounds should play. True to enable sounds, and False to disable them (default value is True).
- ```--closing```: A boolean value indicating whether or not an extra Telegram notification should be sent when the program closes and stops tracking the battery status. True to enable this notification, and False to disable it (default value is True).

It is therefore recommended to create a ```.bat``` file with the following line of code and move this file to the directory that runs files at system startup: ```shell:startup```:

```bash
python BatteryChecker.py --lower 30 --higher 80 --sound True --closing True
```