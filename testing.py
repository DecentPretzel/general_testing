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
    return render_template("Site.html", word="Heyo.")



#Master behavior function
@app.route("/get_behavior", methods=["POST"])
def get_behavior():
    data = request.get_json()
    opinion = data.get("opinion")
    lull = data.get("lull")
    age = data.get("age")
    if opinion == "new": get_agreement()
    else: agreement_ins = ""
    if opinion == "old_conflicting": get_persuasion()
    return agreement_ins



#Determine agreement
def get_agreement():
    normal_agreement_roll = random.randint(0, 100)
    if normal_agreement_roll <= 65: agreement_ins = ""
    else:
        agreement_level = random.choice([0, 25, 50, 75])
        match agreement_level:
            case 0: agreement_ins = "Have your character fully disagree with the opinion of the user's character."
            case 25: agreement_ins = "Have your character mostly disagree with the opinion of the user's character."
            case 50: agreement_ins = "Have your character half-agree with the opinion of the user's character."
            case 75: agreement_ins = "Have your character mostly agree with the opinion of the user's character, but not fully."
    return {"agreement_ins": agreement_ins}



#Determine persuasion
def get_persuasion():
    persuasion_success = random.choice([True, False])
    if persuasion_success:
        persuasion_level = random.choice([25, 50, 75])
    return persuasion_success





#Determine topic change
def get_topic_change():
    data = request.get_json()
    lull = data.get("lull")
    age = data.get("age")
    topic_change_roll = random.randint(0, 100)
    if (lull and topic_change_roll <= 90) or (lull == False and topic_change_roll <= 30):
        topic_change = True
        topic_frequency_roll = random.randint(1, 100)
        if topic_frequency_roll <= 45:
            new_topic = random.choice(["recent_story", "vent", "question"])
        elif topic_frequency_roll <= 80:
            new_topic = random.choice(["gossip", "hobby", "field_of_interest", "realization"])
        else:
            new_topic = random.choice(["old_story", "confiding_question", "compliment", "complaint"])
            ##Determining the character's age in an old story
            if new_topic == "old_story":
                age_in_story = random.uniform(age - age * 0.7, age - age * 0.1)
                return {"topic_change": topic_change, "new_topic": new_topic, "age_in_story": age_in_story}
            ##Determining the level of bias in a compliment or complaint
            if new_topic == "compliment" or new_topic == "complaint":
                bias_roll = random.randint(0, 100)
                if (new_topic == "compliment" and bias_roll <= 40) or (new_topic == "complaint" and bias_roll <= 66):
                    bias = True
                    bias_level = random.randint(1, 2)
                    return {"topic_change": topic_change, "new_topic": new_topic, "bias": bias, "bias_level": bias_level}
                else: bias = False
                return jsonify({"topic_change": topic_change, "new_topic": new_topic, "bias": bias})
        return jsonify({"topic_change": topic_change, "new_topic": new_topic})
    else: topic_change = False
    return jsonify({"topic_change": topic_change})



#Permission to run the site
if __name__ == "__main__":
    app.run(debug=True)