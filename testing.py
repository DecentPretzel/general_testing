#To run the site locally, open the terminal and enter the following...
##cd "/Users/baileyrosenberger/Documents/Sona/SonaGPT Alpha 3"
##deactivate
##rm -rf venv
##python3 -m venv venv
##source venv/bin/activate
##pip install flask (sometimes necessary)
##python3 testing.py
#To then run the locally running site in ngrok, open another terminal and enter this: ngrok http 5000

#To make a change to the live site, save the change in the Python code first, then open a terminal and enter this: git deploy



from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import random



#Create human-visible site template upon opening site
@app.route("/")
def index():
    return render_template("Site.html", word="no reminders.")


#Master behavior function
@app.route("/get_behavior", methods=["POST"])
def get_behavior():
    data = request.get_json()
    in_character = bool(data.get("in_character"))
    opinion = data.get("opinion")
    only_affirmation = bool(data.get("only_affirmation"))
    age = data.get("age")
    if in_character:
        if opinion == "new": agreement_ins = get_agreement()["ins"]
        else: agreement_ins = ""
        if opinion == "old_conflicting": persuasion_ins = get_persuasion()["ins"]
        else: persuasion_ins = ""
        topic_change_ins = get_topic_change(only_affirmation, age)["ins"]
        behavior_instructions = f"{agreement_ins}{persuasion_ins}{topic_change_ins}"
    else: behavior_instructions = ""
    return jsonify({"behavior_instructions": behavior_instructions})



#Determine agreement
def get_agreement():
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
    topic_change_roll = random.randint(0, 100)
    if (only_affirmation and topic_change_roll <= 90) or (only_affirmation == False and topic_change_roll <= 30):
        topic_frequency_roll = random.randint(1, 100)
        if topic_frequency_roll <= 45:
            new_topic = random.choice(["recent_story", "vent", "question"])
        elif topic_frequency_roll <= 80:
            new_topic = random.choice(["gossip", "hobby", "field_of_interest", "realization"])
        else:
            new_topic = random.choice(["old_story", "confiding_question", "compliment", "complaint"])
        match new_topic:
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
    else: ins = ""
    return {"ins": ins}


#Permission to run the site
if __name__ == "__main__":
    app.run(debug=True)