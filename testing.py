#To run the site locally, open the terminal and enter the following...
##cd "/Users/baileyrosenberger/Documents/Sona/SonaGPT Alpha 3"
##deactivate
##rm -rf venv
##python3 -m venv venv
##source venv/bin/activate
##pip install flask (sometimes necessary)
##python3 testing.py
#To then run the locally running site in ngrok, open another terminal and enter this: ngrok http 5000



from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import random



#Create human-visible site template upon opening site
@app.route("/")
def index():
    return render_template("Site.html")



#Agreement Process
@app.route("/get_agreement", methods=["POST"])
def get_agreement():
    normal_agreement_roll = random.randint(0, 100)
    if normal_agreement_roll <= 65:
        normal_agreement = True
        return {"normal_agreement": normal_agreement}
    else:
        normal_agreement = False
        agreement_level = random.randint(0, 99)
    return jsonify({"normal_agreement": normal_agreement, "agreement_level": agreement_level})

@app.route("/get_persuasion", methods=["POST"])
def get_persuasion():
    persuasion_success = random.choice([True, False])
    if persuasion_success:
        persuasion_level = random.randint(1, 100)
        return jsonify({"persuasion_success": persuasion_success, "persuasion_level": persuasion_level})
    return jsonify({"persuasion_success": persuasion_success})



#Topic Change Process
@app.route("/get_topic_change", methods=["POST"])
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