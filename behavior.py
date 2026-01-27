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
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))




#Create human-visible material upon opening site
@app.route("/")
def index():
    return render_template("Site.html", word="Hello world.")




#Write JSON file for emotions
def create_emotions():
    data = {
        "happiness": 10,
        "anger": 0,
        "sadness": 0,
        "fear": 0
    }
    with open("emotions.json", "w") as f:
        json.dump(data, f, indent = 4)




#Master behavior function
@app.route("/get_behavior", methods=["POST"])
def get_behavior():
    #Gather values
    data = request.get_json()
    pleasing = data.get("pleasing")
    angering = data.get("angering")
    saddening = data.get("saddening")
    scaring = data.get("scaring")
    opinion = data.get("opinion")
    farewell = bool(data.get("farewell"))
    only_affirmation = bool(data.get("only_affirmation"))
    age = data.get("age")
    #Determine mood and get mood instruction
    mood_ins = get_mood(pleasing, angering, saddening, scaring)["ins"]
    #If new opinion is said, determine agreement and get agreement instruction
    if opinion == "new":
        agreement_ins = get_agreement()["ins"]
    else:
        agreement_ins = ""
    #If old conflicting opinion is said, determine persuasion and get persuasion instruction
    if opinion == "old_conflicting":
        persuasion_ins = get_persuasion()["ins"]
    else:
        persuasion_ins = ""
    #If no farewell is said, determine topic change and get topic change instruction
    if farewell:
        topic_change_ins = ""
    else:
        topic_change_ins = get_topic_change(only_affirmation, age)["ins"]
    #Combine and deliver instructions to GPT
    behavior_instructions = f"{mood_ins}{agreement_ins}{persuasion_ins}{topic_change_ins}"
    return jsonify({"behavior_instructions": behavior_instructions})




#Determine mood
def get_mood(pleasing, angering, saddening, scaring):
    #Define emotions path
    emotions_path = Path("emotions.json")
    #Create emotions JSON file if it doesn't exist yet
    if not emotions_path.exists():
        create_emotions()
    #Load emotions from JSON file
    with open(emotions_path, "r") as f:
        emotions = json.load(f)
    #Change emotions based on role play context
    emotions["happiness"] += pleasing
    emotions["anger"] += angering
    emotions["sadness"] += saddening
    emotions["fear"] += scaring
    #Keep emotion values within limits
    for key in emotions:
        emotions[key] = clamp(emotions[key], 0, 39)
    #Save emotions to JSON file
    with open(emotions_path, "w") as f: json.dump(emotions, f, indent = 4)
    #Write and return mood instructions
    emotion_descriptions = []
    for emotion in ("happiness", "anger", "sadness", "fear"):
        value = emotions[emotion]
        if value < 10:
            if emotion == "happiness":
                adverb = "un"
            else:
                adverb = "not "
        elif value < 20:
            adverb = "somewhat "
        elif value < 30:
            adverb = ""
        else:
            adverb = "very "
        match emotion:
            case "happiness": adjective = "happy"
            case "anger": adjective = "angry"
            case "sadness": adjective = "sad"
            case "fear": adjective = "afraid / stressed"
        phrase = f"{adverb}{adjective}"
        emotion_descriptions.append(phrase)
    ins = "Ensure that your character's behavior fits their current mood, which is: " + ", ".join(emotion_descriptions) + "."
    return {"ins": ins}




#Determine agreement
def get_agreement():
    #Set agreement grades and their base likelihood scores
    grades = {
        "normal_agreement": 650,
        "overall_agreement": 80,
        "half-agreement": 80,
        "slight_agreement": 80,
        "no_agreement": 80
    }
    #Choose current grade
    current_grade = random.choices(list(grades.keys()), list(grades.values()), k=1)[0]
    #Write instructions regarding current grade
    match current_grade:
        case "normal_agreement": ins = ""
        case "overall_agreement": "Have your character mostly agree with the opinion of the user's character, but not fully. "
        case "half-agreement": "Have your character half-agree with the opinion of the user's character. "
        case "slight_agreement": "Have your character mostly disagree with the opinion of the user's character. "
        case "no_agreement": "Have your character fully disagree with the opinion of the user's character. "
    return {"ins": ins}




#Determine persuasion
def get_persuasion():
    #Set persuasion grades and their base likelihood scores
    grades = {
        "normal_persuasion": 500,
        "overall_persuasion": 120,
        "half-persuasion": 120,
        "slight_persuasion": 120,
        "no_persuasion": 120
    }
    #Choose current grade
    current_grade = random.choices(list(grades.keys()), list(grades.values()), k=1)[0]
    #Write instructions regarding current grade
    match current_grade:
        case "normal_persuasion": ins = ""
        case "overall_persuasion": ins = "Have your character be mostly persuaded by the opinion of the user's character, but not fully. "
        case "half-persuasion": ins = "Have your character be half-persuaded by the opinion of the user's character. "
        case "slight_persuasion": ins = "Have your character be persuaded by the opinion of the user's character, but only slightly."
        case "no_persuasion": ins = "Do not have your character be persuaded by the opinion of the user's character at all."
    return {"ins": ins}




#Determine topic change
def get_topic_change(only_affirmation, age):
    #Set topics and their base likelihood scores
    topics = {
        "none": 800,
        "question": 50,
        "confiding_question":10,
        "compliment": 10,
        "complaint": 10,
        "realization": 30,
        "recent_story": 50,
        "old_story": 10,
        "gossip": 30,
        "hobby": 30,
        "field_of_interest": 30,
        "vent": 50
    }
    #Increase chance of topic change if user message was only affirmation
    if only_affirmation:
        topics["none"] -= 700
    #Choose new topic
    new_topic = random.choices(list(topics.keys()), weights = list(topics.values()), k=1)[0]
    #Write instructions regarding new topic
    match new_topic:
        case "none": ins = ""
        case "question": ins = "Have your character ask a question - don't have your character introduce this question with the word \"question\", don't have your character repeat a previous question, and ensure that this question fits the current mood. "
        case "confiding_question": ins = "Have your character ask a question regarding something they're self-conscious about (i.e., \"Do you think I'm fat?\", \"Am I too rude?\") - don't have your character introduce this question with the word \"confide\", \"question\", or any inflection of those, don't have your character repeat a previous question, and ensure that this question fits the current mood. "
        case "compliment":
            bias_roll = random.randint(0, 100)
            if bias_roll <= 45:
                bias_level = random.randint(1, 2)
                match bias_level:
                    case 1: bias_ins = "make the compliment somewhat twinged with personal bias befitting your character, "
                    case 2: bias_ins = "make this compliment heavily influenced by personal bias befitting your character, "
            else:
                bias_ins = ""
            ins = f"Have your character compliment the user's character - {bias_ins}don't have your character introduce this topic with the word \"compliment\", don't have your character repeat a previous compliment, and ensure that this new topic fits the current mood. "
        case "complaint":
            bias_roll = random.randint(0, 100)
            if bias_roll <= 66:
                bias_level = random.randint(1, 2)
                match bias_level:
                    case 1: bias_ins = "make the complaint somewhat twinged with personal bias befitting your character, "
                    case 2: bias_ins = "make this complaint heavily influenced by personal bias befitting your character, "
            else:
                bias_ins = ""
            ins = f"Have your character mention a complaint regarding something they wish the player's character would do differently or better - {bias_ins}don't have your character introduce this topic with the word \"complain\" or \"complaint\", don't have your character repeat a previous complaint, and ensure that this new topic fits the current mood. "
        case "realization": ins = "Have your character mention something they just realized - don't have your character introduce this topic with the word \"realize\", \"realization\", or any inflection of those, don't have your character repeat a previous realization, and ensure that this new topic fits the current mood. "
        case "recent_story": ins = "Have your character mention a story from earlier that day or recently - don't have your character introduce this topic with the word \"story\", don't have your character repeat a previous story, and ensure that this new topic fits the current mood. "
        case "old_story":
            age_in_story = random.uniform(age - age * 0.7, age - age * 0.1)
            ins = f"Have your character mention a story from when they were {age_in_story} years old - don't have your character introduce this topic with the word \"story\", don't have your character repeat a previous story, and ensure that this new topic fits the current mood. Don't have your character mention their exact age in the story; instead, have them mention roughly how long ago it took place (i.e., \"a couple years ago\", \"a few years ago\") or when it took place (i.e., \"when I was a kid\", \"after I moved to California\", \"during the Great Depression\"). "
        case "gossip": ins = "Have your character mention gossip about one or more acquaintances - don't have your character introduce this topic with the word \"gossip\", don't have your character repeat a previous bit of gossip, and ensure that this new topic fits the current mood. "
        case "hobby": ins = "Have your character talk about something regarding their hobby - don't have your character introduce this topic with the word \"hobby\", don't have your character repeat a previous bit about their hobby, and ensure that this new topic fits the current mood. "
        case "field_of_interest": ins = "Have your character talk about something regarding their field of interest - don't have your character introduce this topic with the word \"field\" or \"interest\", don't have your character repeat a previous bit about their interest, and ensure that this new topic fits the current mood. "
        case "vent": ins = "Have your character vent about something - don't have your character introduce this topic with the word \"vent\", don't have your character repeat a previous vent, and ensure that this new topic fits the current mood. "
    return {"ins": ins}




#Permission to run the site
if __name__ == "__main__":
    app.run(debug=True)