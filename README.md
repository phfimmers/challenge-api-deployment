# Challenge-api-deployment
The real estate company ['ImmoEliza'](https://immoelissa.be/) was really happy about our previously made regression model. They would like you to create an API to let their web-devs create a website around it.

# Description (why)
Housing prices prediction is an essential element for an economy. Analysis of price ranges influence both sellers and buyers. 

Our [previous project](https://github.com/FrancescoMariottini/Belgium-prices-prediction/settings) created a Linear Regression model to estimate the price of the house accurately with the given features. Within this project an online API to run the price prediction is made. 

# Target audience (to whom)
['ImmoEliza'](https://immoelissa.be/) web developers to receive price prediction based on input values provided by a user.

# Objectives (what)
1. Be able to deploy a machine learning model.
2. Be able to create a Flask API that can handle a machine learning model.
3. Deploy an API to Heroku with Docker.

Project evalution is based on the compliance to the following criteria:

|Criteria|Indicator|
|---|---| 
|Is complete|Your API works.|	
||Your API is wrapped in a Docker image.|
||Pimp up the readme. (what, why, how, who).|
||Your model predict.|
||Your API is deployed on Heroku.|
|Is good |The repo doesn't contain unnecessary files.|
||You used typing.|
||The presentation is clean.|
||The web-dev group understood well how your API works.|


# Development (how)
Input requirements for the web developers were initially agreed with the other Becode teams. Then the team agreed on how to fulfill and split the required development steps among its members. Step 0 (team management) was added.

0. Team organization
1. Project preparation
2. Pre-processing pipeline
3. Fit your data!
4. Create your API
5. Create a Dockerfile to wrap your API
6. Deploy your Docker image in Heroku
7. Document your API

For step 2 and 3 [source files](https://github.com/FrancescoMariottini/Belgium-prices-prediction/tree/main/source) from the previous project were used as basis after adapting them in in line with the JSON input requirements.


## Input requirements
Hereby follow the agreed requirements for the json to be provided by the web developers:

```json
{
"data": {
"area": int,
"property-type": "APARTMENT" | "HOUSE" | "OTHERS",
"rooms-number": int,
"zip-code": int,
"land-area": Optional[int],
"garden": Optional[bool],
"garden-area": Optional[int],
"equipped-kitchen": Optional[bool],
"full-address": Optional[str],
"swimmingpool": Opional[bool],
"furnished": Opional[bool],
"open-fire": Optional[bool],
"terrace": Optional[bool],
"terrace-area": Optional[int],
"facades-number": Optional[int],
"building-state": Optional["NEW" | "GOOD" | "TO RENOVATE" | "JUST RENOVATED" | "TO REBUILD"]
}
}
```
Output requirements were not strictly fixed but rather delegated to each team after sharing a reference template:

```json
{
    "prediction": Optional[float],
    "error": Optional[str]
}
```
A HTTP status code is also provided in case of error.
## Step 0: Team organization ##
In the introduction meeting it emerged that team members were looking for an organisation to avoid overlaps and meet project requirements without rushing for it.
A Trello board (Kanban template) was organised and team members agreed on how to split the required development steps. For each step was responsible person was chosen, support could be provided if requested.
Morning meeting were scheduled to check the status of the project and plan the day activites. Afternon meetings were scheduled at lunch if morning tasks were completed to set up new goal.
An interim review was set up on 4/12/20 to upload an already working version before refining it. 
A trello list with general useful links, guidelines and tips was also provided.


## Step 1: Project preparation ##
A repository was prepared to fullfill the required requirements: 
1. Create a folder to handle your project.
1. Create a file app.py that will contain the code for your API.
1. Create a folder preprocessing that will contain all the code to preprocess your data.
1. Create a folder model that will contain your model.
1. Create a folder predict that will contain all the code to predict a price.

All these main folders, exclusively dedicated to the api, were created in a **source** folder. Additional folders (**assets**, **data**, **docs** and **outpus**) were created for the project.


## Step 2: Pre-processing pipeline ##
This python module contains all the code to preprocess the data. The file cleaning_data.py contains all the code used to preprocess the data received to predict a new price (fill the nan, handle text data,...). The file contains a function preprocess() that takes a new house's data as input and returns those data preprocessed as output.
If data doesn't contain the required information, an error is returned to the user.

## Step 3: Fit your data! ##
In the predict folder a file prediction.py contains all the code used to predict a new house's price. The file contains a function predict() that takes the preprocessed data as an input and returns a price as output.

## Step 4: Create your API ##
In the app.py file, the Flask API contains:
* A route at / that accept:
    * GET request and return "alive" if the server is alive.
* A route at /predict that accept:
    * POST request that receives the data of a house in json format.
    * GET request returning a string to explain what the POST expect (data and format).

## Step 5: Create a Dockerfile to wrap your API ##
To deploy the API Docker was used.
The Dockerfile created an image with Ubuntu and Python 3.8 plus all the required dependencies for the created code:
library|version
click|7.1.2
Flask|1.1.2
gunicorn|20.0.4
itsdangerous|1.1.0
Jinja2|2.11.2
MarkupSafe|1.1.1
marshmallow|3.9.1
numpy|1.19.4
pandas|1.1.4
python-dateutil|2.8.1
pytz|2020.4
six|1.15.0
Werkzeug|1.0.1

## Step 6: Deploy your Docker image in Heroku ##
Heroku allowed to push the docker container on their server and to start it (more information [here](https://github.com/becodeorg/BXL-Bouman-2.22/tree/master/content/05.deployment/4.Web_Application)).

## Step 7: Document your API ##
A clear readme was made to explain to the web developers where the API is hosted and how to interact with it.

A ppt presentation is available at ... 

## FAQ ##
Hereby follow the answers to the main questions about the API.

*What routes are available? With which methods?*

*What kind of data is expected (How should they be formatted?*

*What is mandatory or not?*

*What is the output of each route in case of success?*

*What is the output in case of error?*

#### Date of Completion: 
8/12/2020 (code)
14/12/2020 (presentation)

# Team:
Ankita
Francesco
Opaps
Philippe
