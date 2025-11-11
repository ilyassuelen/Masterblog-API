from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os

app = Flask(__name__)
CORS(app)

POSTS_FILE = "posts.json"


def load_posts():
    """Read all posts from the JSON file. Return a list of posts."""
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_posts(posts):
    """Writes the list of posts to the JSON file."""
    with open(POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4)


def find_post_by_id(posts, post_id):
  """ Find the post with the id 'post_id'.
  If there is no post with this id, return None. """
  for post in posts:
    if post["id"] == post_id:
      return post
  return None


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Return all blog posts with optional query parameters"""
    posts = load_posts()
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc').lower()

    # Return original order if no sorting parameter
    if not sort_field:
        return jsonify(posts)

    if sort_field not in {'title', 'content'} or direction not in {'asc', 'desc'}:
        return jsonify({"error": "Invalid sort or direction parameter."}), 400

    # Sort posts by the selected field and direction
    sorted_posts = sorted(
        posts,
        key=lambda p: p[sort_field].lower(),
        reverse=(direction == 'desc')
    )
    return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def post_posts():
    """Create a new blog post with a title and content, and save it to the JSON file."""
    posts = load_posts()
    data = request.get_json()

    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400

    # Create unique ID for post
    new_id = max((post["id"] for post in posts), default=0) + 1

    new_post = {
        "id": new_id,
        "title": title,
        "content": content
    }

    posts.append(new_post)
    save_posts(posts)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_posts(id):
    """Delete a blog post by ID. Return success or 404 if not found."""
    posts = load_posts()
    post = find_post_by_id(posts, id)

    if post is None:
        return jsonify({"message": f"Post with id {id} not found."}), 404

    posts.remove(post)
    save_posts(posts)

    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_posts(id):
    """Update an existing blog post."""
    posts = load_posts()
    post = find_post_by_id(posts, id)

    if post is None:
        return jsonify({"message": f"Post with id {id} not found."}), 404

    data = request.get_json()
    post['title'] = data.get('title', post['title'])
    post['content'] = data.get('content', post['content'])

    save_posts(posts)

    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """Search posts by title or content."""
    posts = load_posts()

    # Query-Parameter
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # If neither title nor content parameters are specified return empty list
    if not title_query and not content_query:
        return jsonify([])

    # Filter posts that match the search query
    results = []
    for post in posts:
        title_matches = title_query and title_query in post['title'].lower()
        content_matches = content_query and content_query in post['content'].lower()

        # Append only, if at least one condition is met
        if title_matches or content_matches:
            results.append(post)

    return jsonify(results), 200


# Swagger UI configuration
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Masterblog API"
    }
)

# Register Swagger Blueprint
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
