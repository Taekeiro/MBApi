from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort', None)
    sort_direction = request.args.get('direction', 'asc').lower()

    if sort_field:
        if sort_field not in ['title', 'content']:
            return jsonify({"error": f"Invalid sort field '{sort_field}'. Allowed values are 'title' or 'content'."}), 400

        if sort_direction not in ['asc', 'desc']:
            return jsonify({"error": f"Invalid sort direction '{sort_direction}'. Allowed values are 'asc' or 'desc'."}), 400

        reverse = sort_direction == 'desc'
        sorted_posts = sorted(POSTS, key=lambda x: x[sort_field].lower(), reverse=reverse)
        return jsonify(sorted_posts), 200

    return jsonify(POSTS), 200



@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.json

    # Validate input
    if not data or "title" not in data or "content" not in data:
        missing_fields = [field for field in ["title", "content"] if field not in data]
        return jsonify({"error": "Missing fields", "missing": missing_fields}), 400

    # Generate a new unique ID
    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1

    # Create a new post
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }
    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    global POSTS
    post = next((post for post in POSTS if post['id'] == post_id), None)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS = [post for post in POSTS if post['id'] != post_id]
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    global POSTS
    post = next((post for post in POSTS if post['id'] == post_id), None)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    data = request.json
    # Update fields only if provided
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # Filter posts based on provided title and content queries
    filtered_posts = [
        post for post in POSTS
        if (title_query and title_query in post["title"].lower()) or
           (content_query and content_query in post["content"].lower())
    ]

    return jsonify(filtered_posts), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
