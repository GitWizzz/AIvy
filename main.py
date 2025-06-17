from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import google.generativeai as genai

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://kunalk9521:FTRzVtcqcIRUgIox@devlopment.eu1u1os.mongodb.net/chatgbt"
mongo = PyMongo(app)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

@app.route("/")
def home():
    chats = mongo.db.chats.find({})
    my_chats = [chat for chat in chats]
    print(f"Chats retrieved from database: {my_chats}") 
    return render_template("index.html", my_chats=my_chats)

@app.route("/api", methods=["POST"])
def qa():
    if "question" not in request.json:
        return jsonify({"error": "Question field is missing"}), 400

    question = request.json["question"]
    print(f"Question received: {question}")  

   
    chat = mongo.db.chats.find_one({"question": question})
    if chat:
        print(f"Found answer in database: {chat['answer']}")  
        return jsonify({"question": question, "answer": chat["answer"]})


    convo = model.start_chat(history=[])
    print(f"Conversation started: {convo}")  
    convo.send_message(question)
    print(f"Question sent to model: {question}")  
    response_text = convo.last.text
    print(f"Response received from model: {response_text}")  

    
    mongo.db.chats.insert_one({"question": question, "answer": response_text})

    return jsonify({"question": question, "answer": response_text})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
