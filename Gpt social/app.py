from flask import Flask, request, jsonify, send_from_directory
import openai

openai.api_key = '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'

app = Flask(__name__, static_url_path='')
posts = []

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
def index():
    return send_from_directory('static', 'index.html')

@app.route('/create_post', methods=['POST'])
def create_post():
    content = request.form.get('content')
    print(f"Received post content: {content}")

    ai_comments = []
    if '#gpt' in content:
        message = content.replace('#gpt', "").strip()
        print(f"Processing AI message: {message}")
        ai_comment = get_ai_response(message)
        ai_comments.append(ai_comment)
        print(f"AI comment added to post: {ai_comment}")

    new_post = {
        'content': content,
        'comments': ai_comments
    }
    posts.append(new_post)

    return jsonify(success=True)

@app.route('/create_comment', methods=['POST'])
def create_comment():
    content = request.form.get('content')
    post_id = request.form.get('post_id')
    print(f"Received comment content: {content} for post with id: {post_id}")

    ai_comments = []
    if '#gpt' in content:
        message = content.replace('#gpt', "").strip()
        print(f"Processing AI message: {message}")
        ai_comment = get_ai_response(message)
        ai_comments.append(ai_comment)
        print(f"AI comment added: {ai_comment}")

    for post in posts:
        if post_id == str(id(post)):
            post['comments'].append(content)
            break

    return jsonify(success=True)

@app.route('/get_posts', methods=['GET'])
def get_posts():
    print("Fetching all posts.")
    return jsonify(posts)

if __name__ == "__main__":
    print("Starting the application")
    app.run(port=5004, debug=True)
