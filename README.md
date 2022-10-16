# Electrical Project Manager

#### Video Demo:  https://www.youtube.com/watch?v=avjYKTV_CRg

## Description:
This web app can be used to generate and manage electrical studies and projects.

In my work routine as an electrical engineer, I develop projects related to high voltage in which detailed studies are required. So I created this app that serves as a tool to facilitate this work.

This app is intended for technicians and engineers and allows the development of their electrical projects, and from there automatically generates an analysis regarding the ANSI point of transformers, ANSI 50 (Instantaneous Overcurrent Relay) / 51 (AC Time Overcurrent Relay) protections, the graph of the IEC IDMT (Inverse Definite Minimum Time) curve, and coordination of protections, according, but not limited, to the standards:
- IEC 60255: Measuring relays and protection equipment
- IEEE C57.109: Guide For Liquid-Immersed Transformers Through-Fault-Current Duration
  
<br>
  
## Built With:
- `Python`
- `Flask Web Framework`
- `Jinja`
- `SQLite`
- `chart.js`

<br>

## Directory structure:
- The **static** folder contains the static CSS, Javascript and image files;
- The **templates** folder contains the HTML templates powered by Jinja template engine and chart.js to make the HTML-based charts.;
- The **app.py** file is the main file of the app and it uses Flask web framework to route the web pages and do the backend;
-  The **electric.db** file is an SQLite database where is stored all users' auth and projects data. 

<br>


## Getting Started:
First is necessary to have python installed on your machine.<br>
In the application root directory:

1. Create a Virtual Environment: 
```sh
python -m venv venv
```

2. Activate the Virtual Environment created in the previous step:
<br>

on Linux / MacOS:

```sh
. venv/bin/activate
```

on Windows:

```sh
. venv\Scripts\activate
```

3. Ensure your environment has pip installed:
```sh
python -m ensurepip
```

4. Install this libraries:
```sh
pip install Flask
```
```sh
pip install flask_session
```
```sh
pip install cs50
```
```sh
pip install pywebview
```
<br>

## Usage:
With all prerequisites satisfied you can run the application with:
```sh
flask run
```

<br>

If successful, you should see in the terminal the local address which the server is running, in your browser go to this address.

At the first use, you have to register, choose a username and password, the password must meet the prerequisites shown on the page.

After logging in you will be able to create your first project. To create a project is necessary first an electric profile, go to the **profiles** page and create a new profile. 

The profile will define the calculation constants, after filling all the fields go to the **projects** page and create a new project. 

To properly create a project is obligatory selecting a profile, setting the voltage, demand and power factor, you will be able to select the profile you just created, selecting a customer is optional, if you want you can create one on the **customers** page. Setting the fault data is optional, if not set you won't be able to analyze the coordination of protection related to it.

On the next page, you should define the power transformers, click on **add new transformer**, you can add how many you want, setting the power, impedance and type for each is obligatory, is necessary at least one transformer defined to proceed to the next page.

After saving the project you be able to proceed to **Diagram** page, this page shows the compiled information related to the electrical analysis on the project.

It includes the calculation of the ANSI point of each transformer, the nominal and magnetization currents, the analysis regarding the ANSI 50 (Instantaneous Overcurrent Relay) and 51 (AC Time Overcurrent Relay) protections, trip and pickup currents, and the graph of the IEC IDMT curve.



