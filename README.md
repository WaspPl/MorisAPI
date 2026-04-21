
# Moris API
This repository contains the API used to build your own desktop smart assistant. </br>
Supported features include:

1. [Multiple users creation with role assignment](#multiple-users-creation-with-role-assignment)
2. [Authorization](#authorization)
3. [Privileges](#privileges)
4. [Custom command creation with role privileges](#custom-command-creation-with-role-privileges)
5. [Custom Python script execution using prompts](#custom-python-script-execution-using-prompts)
6. [Display support](#display-support)
7. [YAML Config](#yaml-config)

## API Documentation and Quick Start
This project uses FastAPI's automatic documentation. Once the server is running, you can access the full interactive API reference here:

* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
### Quick Start
#### 1. Clone & Install
```bash
git clone [https://github.com/WaspPl/MorisAPI.git](https://github.com/WaspPl/MorisAPI.git)
cd MorisAPI
pip install -r requirements.txt
```
#### 2. Run the API
```bash
python src/main.py
```
## Multiple users creation with role assignment
The API allows you to create multiple users and roles they can be assigned to. </br>
The users created this way can be used log in to the system and send messages to the assistant. </br>
After the first run the database will be prepopulated with: 
- a default admin user that can be edited and deleted later (unless its the ONLY admin account present)
```
id: 1
username: admin
password: admin
role_id: 1
```
- 2 default roles, that can be renamed but not deleted
```
id: 1
name: admin
```
```
id: 2
name: user
```
## Authorization
Every created user has an option to log into the system and acquire an access token. </br>
The duration of the token depends on a per-user variable ```access_token_duration_minutes``` that can be changed by the admin. This is so that it's possible to create home automations using those tokens easily by setting the value to a long period of time. This practice is however NOT recommended for human user profiles, as if the token gets stolen the malicious actor gets access to all of this user's commands and privileges. </br>
If you want to use a short access token duration value for automations this API also supplies a ```refresh_token``` upon login, that can be used to refresh your access token. This token's duration is configured in the config.yaml file and should be much longer than the access token's. </br>
 
## Privileges
A user with an admin role (id=1) has these privileges:
- Permission to execute CREATE, UPDATE and DELETE operations on other database elements
-  Automatic permission to view and execute every command added to the system

Users with any other role only have permission to view and execute commands and other elements assigned to their role. </br>
While new roles with new privileges can be created it is intentionally impossible to create a new role with edit permissions.
## Custom command creation with role privileges
Just as one can create new users and roles, one can also create new commands, which are the whole point of the system. </br>
A single command consists of:
| name| description |
|--|--|
| name | a name used to identify the command |
| description | a description used to... describe what the command does. It should let the user know when and how to use it. |
| sprite_id |  an id of a sprite that should be sent to displays when the command executes (more on that later) |
| sprite_repeat_times | a numberic value describing how many times the selected sprite should play |
| is_output_llm | a boolean value that lets you specify whether the script's output should be passed on to an LLM |
| llm_prefix | if the output is passed to an LLM this message prefixes it. If the script output reads 'apple' and the llm_prefix is 'tell me you ate an ' the message sent becomes 'tell me you ate an apple' |
and values stored in other tables:
| name | description |
|--|--|
| script | a python script that will be executed when the command runs. The output of the script is whatever it prints to the console |
| a list of prompts | a list of prompts that make the API execute the command. It supports regex groups allowing you to pass on arguments to your scripts. |
| a list of roles | a list of roles that determine which users can execute and see the command and it's sprite. |

## Custom Python script execution using prompts
The whole point of the system is to allow users to execute python scripts remotely through messages. </br>
When a message is received through the ```/messages``` endpoint it gets compared to prompts the user who sent is can use. When it finds a match the script belonging to the command gets executed with values inside regex groups (or named regex groups) passed on as parameters.</br>
These parameters can then be retrieved by the script and used in it's execution</br>
Example:
Script
```python
import  sys
import  json

raw_data  =  sys.argv[1]
data  =  json.loads(raw_data)
city  =  data.get("city")

temp  =  20  # this is where you put actual logic

print(f"The temperature in {city} is {temp} degrees.")
```
Prompt
```regex
what's the weather in (?P<city>.+)
```
Sending a message saying 
```
what's the weather in Gdańsk
```
 returns 
 ```
 The temperature in Gdańsk is 20 degrees.
 ```
 If no prompt matches the message it get's passed to an LLM.
## Display support
In order to bring more life into the API it's been made fully compatible with MALDC, a dedicated display controller for Raspberry PI that allows for display of responses and accompanied sprites. </br>
A sprite get's sent as a base64 converted sprite sheet and displays while the assistant talks.</br>
While i highly recommend giving MALDC a try I've made it possible to turn the display feature off or change the address to which the display data gets sent making it possible for use with other displays
## YAML Config
Customizability is the name of the game for me, so I've put a lot of effort to make sure as many things can be controlled through a .yaml config file as possible. </br>
After first running the API a ```config.yaml``` file will be created making it possible to adjust your storage, LLM, display, authorization and host settings.
