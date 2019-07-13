# Carleton - No More Waitlist
Do you want to get into a course that's full? Are you tired of constantly checking if room has opened up? Why not automate it. 

## What does this do?
- Automatically attempts to sign up for courses
- Send email notifications

This program works best when combined with a task scheduler (ie. chron job or windows task scheduler)

## Demo
Note: My laptop is old.
![](docs/assets/demo_carleton_central_automation.gif)


## Install and Usage
1. Download the code and install dependencies.
  ```
  git clone https://github.com/altear/carleton-no-more-waitlist.git
  cd carleton-no-more-waitlist
  pipenv install
  ```
2. Rename the config.yaml.template file as config.yaml. Then update it with your MyCarleton username, password, and the courses you want to sign up for.
3. Try running it.
  ```
  pipenv run python main.py
  ```
4. Set up a scheduled task to run the script.

Useful: the configuration has an option to run the browser in headless mode.