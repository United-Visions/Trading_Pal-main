from flask import Flask, request, jsonify, send_from_directory
import csv
import openai

openai.api_key = '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'

app = Flask(__name__, static_url_path='')

# Function to get AI response
def get_ai_response(message):
    try:
        print("Generating AI response...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        )
        ai_response = response.choices[0].message['content']
        print("AI response generated.")
        return ai_response
    except Exception as e:
        print("Error generating AI response: ", str(e))
        return ''

@app.route('/')
def home():
    print("Home route accessed")
    return send_from_directory('static', 'index.html')

@app.route('/post_message', methods=['POST'])
def post_message():
    user_message = request.json['user_message']
    print(f"Received user message: {user_message}")

    comments = []
    if '#heytradingpal' in user_message:
        message = user_message.replace('#heytradingpal', "").strip()
        print(f"Processing user message: {message}")
        ai_response = get_ai_response(message)
        comments.append("TradingPal: " + ai_response)
        print(f"Added AI comment to post: {ai_response}")

    try:
        with open('user_posts.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user_message, comments])
            print(f"Saved post to CSV: {user_message}, {comments}")
    except Exception as e:
        print("Error writing to CSV file: ", str(e))

    return jsonify({'user_message': user_message, 'comments': comments})

@app.route('/post_comment', methods=['POST'])
def post_comment():
    user_comment = request.json['comment']
    print(f"Received user comment: {user_comment}")

    ai_comment = ''
    if '#heytradingpal' in user_comment:
        message = user_comment.replace('#heytradingpal', "").strip()
        print(f"Processing user comment: {message}")
        ai_comment = "TradingPal: " + get_ai_response(message)
        print(f"Generated AI comment: {ai_comment}")

    return jsonify({'ai_comment': ai_comment})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    print("Fetching all messages from CSV file")
    try:
        with open('user_posts.csv') as file:
            posts = list(csv.reader(file))
        print(f"Fetched {len(posts)} posts")
        return jsonify(posts)
    except Exception as e:
        print("Error reading from CSV file: ", str(e))
        return jsonify([])

if __name__ == '__main__':
    with app.app_context():
        print("Starting the application")
        app.run(port=5004, debug=True)
