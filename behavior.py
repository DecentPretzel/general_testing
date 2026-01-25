#To run the site locally, open the terminal and enter the following...
##cd "/Users/baileyrosenberger/Documents/Sona/General Testing"
##deactivate
##rm -rf venv
##python3 -m venv venv
##source venv/bin/activate
##pip install flask (sometimes necessary)
##python3 behavior.py
#To then run the locally running site in ngrok, open another terminal and enter this: ngrok http 5000
#To make a change to the live site, save the change in the Python code first, then open a terminal and enter this: git deploy




#Basic setup
from pathlib import Path
import json
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import random
import math





#Create human-visible material upon opening site
@app.route("/")
def index(): return render_template("Site.html", word="Hello world.")




#Write JSON file for emotions
def write_emotions():
    data = {
        "happiness": 10,
        "anger": 0,
        "sadness": 0,
        "fear": 0
    }
    with open("emotions.json", "w") as f: json.dump(data, f, indent = 4)





#Master behavior function
@app.route("/get_behavior", methods=["POST"])
def get_behavior():
    #Gather values
    data = request.get_json()
    pleasing_content = data.get("pleasing_content")
    angering_content = data.get("angering_content")
    saddening_content = data.get("saddening_content")
    scaring_content = data.get("scaring_content")
    opinion = data.get("opinion")
    farewell = bool(data.get("farewell"))
    only_affirmation = bool(data.get("only_affirmation"))
    age = data.get("age")
    #Determine mood and get mood instruction
    mood_ins = get_mood(pleasing_content, angering_content, saddening_content, scaring_content)["ins"]
    #If new opinion is said, determine agreement and get agreement instruction
    if opinion == "new": agreement_ins = get_agreement()["ins"]
    else: agreement_ins = ""
    #If old conflicting opinion is said, determine persuasion and get persuasion instruction
    if opinion == "old_conflicting": persuasion_ins = get_persuasion()["ins"]
    else: persuasion_ins = ""
    #If no farewell is said, determine topic change and get topic change instruction
    if farewell: topic_change_ins = ""
    else: topic_change_ins = get_topic_change(only_affirmation, age)["ins"]
    #Combine and deliver instructions to GPT
    behavior_instructions = f"{mood_ins}{agreement_ins}{persuasion_ins}{topic_change_ins}"
    return jsonify({"behavior_instructions": behavior_instructions})




#Determine mood
def get_mood(pleasing_content, angering_content, saddening_content, scaring_content):
    #Load emotions from JSON file and rename them for efficiency
    with open("emotions.json", "r") as f: emotions = json.load(f)
    happiness = emotions["happiness"]
    anger = emotions["anger"]
    sadness = emotions["sadness"]
    fear = emotions["fear"]
    #Change emotions based on role play context
    happiness += pleasing_content
    anger += angering_content
    sadness += saddening_content
    fear += scaring_content
    #Keep emotion values within limits
    min = 0
    max = 39
    for emotion in emotions:
        if emotion < min: emotion = min
        if emotion > max: emotion = max
    #Name emotions back and save them to JSON file
    emotions["happiness"] = happiness
    emotions["anger"] = anger
    emotions["sadness"] = sadness
    emotions["fear"] = fear
    with open("emotions.json", "w") as f: json.dump(emotions, f, indent = 4)
    #Write and return mood instructions
    very_low = range(min, 9)
    low = range(10, 19)
    medium = range(20, 29)
    high = range(30, max)
    if happiness == very_low: happiness_des = "unhappy, "
    if happiness == low: happiness_des = "somewhat happy "
    if happiness == medium: happiness_des = "happy, "
    if happiness == high: happiness_des = "very happy, "
    if anger == very_low: anger_des = "not angry, "
    if anger == low: anger_des = "somewhat angry, "
    if anger == medium: anger_des = "angry, "
    if anger == high: anger_des = "very angry, "
    if sadness == very_low: sadness_des = "not sad, "
    if sadness == low: sadness_des = "somewhat sad, "
    if sadness == medium: sadness_des = "sad, "
    if sadness == high: sadness_des = "very sad, "
    if fear == very_low: fear_des = "not afraid / stressed. "
    if fear == low: fear_des = "somewhat afraid / stressed. "
    if fear == medium: fear_des = "afraid / stressed. "
    if fear == high: fear_des = "very afraid / stressed. "
    ins = f"Ensure that your character's tone fits their current mood, which is: {happiness_des}{anger_des}{sadness_des}{fear_des}"
    return ins




#Determine agreement
def get_agreement():
    #Roll to see if disagreement will occur
    normal_agreement_roll = random.randint(0, 100)
    if normal_agreement_roll <= 65: ins = ""
    else:
        agreement_level = random.choice([0, 25, 50, 75])
        match agreement_level:
            case 0: ins = "Have your character fully disagree with the opinion of the user's character. "
            case 25: ins = "Have your character mostly disagree with the opinion of the user's character. "
            case 50: ins = "Have your character half-agree with the opinion of the user's character. "
            case 75: ins = "Have your character mostly agree with the opinion of the user's character, but not fully. "
    return {"ins": ins}




#Determine persuasion
def get_persuasion():
    #Roll to see if persuasion will occur
    persuasion_success_roll = random.randint(0, 100)
    if persuasion_success_roll <= 50:
        persuasion_level = random.choice([25, 50, 75])
        match persuasion_level:
            case 25: ins = "Have your character be persuaded by the opinion of the user's character, but only slightly. "
            case 50: ins = "Have your character be half-persuaded by the opinion of the user's character. "
            case 75: ins = "Have your character be mostly persuaded by the opinion of the user's character, but not fully. "
    else: ins = ""
    return {"ins": ins}




#Determine topic change
def get_topic_change(only_affirmation, age):
    topics = {
        "none": 750,
        "question": 50,
        "confiding_question":10,
        "compliment": 10,
        "complaint": 10,
        "recent_story": 10,
        "old_story": 10,
        "gossip": 30,
        "hobby": 30,
        "field_of_interest": 30,
        "vent": 50
    }
    if only_affirmation: topics["none"] -= 650
    new_topic = random.choices(list(topics.keys()), weights = list(topics.values()), k = 1)[0]
    match new_topic:
        case "none": ins = ""
        case "recent_story": ins = "Have your character mention a story from earlier that day or recently - don't have your character introduce this topic with the word \"story\", don't have your character repeat a previous story, and ensure that this new topic fits the current mood. "
        case "vent": ins = "Have your character vent about something - don't have your character introduce this topic with the word \"vent\", don't have your character repeat a previous vent, and ensure that this new topic fits the current mood. "
        case "question": ins = "Have your ask a question - don't have your character introduce this question with the word \"question\", don't have your character repeat a previous question, and ensure that this question fits the current mood. "
        case "gossip": ins = "Have your character mention gossip about one or more acquaintances - don't have your character introduce this topic with the word \"gossip\", don't have your character repeat a previous bit of gossip, and ensure that this new topic fits the current mood. "
        case "hobby": ins = "Have your character talk about something regarding their hobby - don't have your character introduce this topic with the word \"hobby\", don't have your character repeat a previous bit about their hobby, and ensure that this new topic fits the current mood. "
        case "field_of_interest": ins = "Have your character talk about something regarding their field of interest - don't have your character introduce this topic with the word \"field\" or \"interest\", don't have your character repeat a previous bit about their interest, and ensure that this new topic fits the current mood. "
        case "realization": ins = "Have your character mention something they just realized - don't have your character introduce this topic with the word \"realize\", \"realization\", or any inflection of those, don't have your character repeat a previous realization, and ensure that this new topic fits the current mood. "
        case "old_story":
            age_in_story = random.uniform(age - age * 0.7, age - age * 0.1)
            ins = f"Have your character mention a story from when they were {age_in_story} years old - don't have your character introduce this topic with the word \"story\", don't have your character repeat a previous story, and ensure that this new topic fits the current mood. Don't have your character mention their exact age in the story; instead, have them mention roughly how long ago it took place (i.e., \"a couple years ago\", \"a few years ago\") or when it took place (i.e., \"when I was a kid\", \"after I moved to California\", \"during the Great Depression\"). "
        case "confiding_question": ins = "Have your character ask a question regarding something they're self-conscious about (i.e., \"Do you think I'm fat?\", \"Am I too rude?\") - don't have your character introduce this question with the word \"confide\", \"question\", or any inflection of those, don't have your character repeat a previous question, and ensure that this question fits the current mood. "
        case "compliment":
            bias_roll = random.randint(0, 100)
            if bias_roll <= 45:
                bias_level = random.randint(1, 2)
                match bias_level:
                    case 1: bias_ins = "make the compliment somewhat twinged with personal bias befitting your character, "
                    case 2: bias_ins = "make this compliment heavily influenced by personal bias befitting your character, "
            else: bias_ins = ""
            ins = f"Have your character compliment the user's character - {bias_ins}don't have your character introduce this topic with the word \"compliment\", don't have your character repeat a previous compliment, and ensure that this new topic fits the current mood. "
        case "complaint":
            bias_roll = random.randint(0, 100)
            if bias_roll <= 33:
                bias_level = random.randint(1, 2)
                match bias_level:
                    case 1: bias_ins = "make the complaint somewhat twinged with personal bias befitting your character, "
                    case 2: bias_ins = "make this complaint heavily influenced by personal bias befitting your character, "
            else: bias_ins = ""
            ins = f"Have your character mention a complaint regarding something they wish the player's character would do differently or better - {bias_ins}don't have your character introduce this topic with the word \"complain\" or \"complaint\", don't have your character repeat a previous complaint, and ensure that this new topic fits the current mood. "
    return {"ins": ins}




#Permission to run the site
if __name__ == "__main__":
    app.run(debug=True)