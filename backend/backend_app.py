from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc').lower()

    if not sort_field:
        return jsonify(POSTS)

    if sort_field not in {'title', 'content'} or direction not in {'asc', 'desc'}:
        return jsonify({"error": "Invalid sort or direction parameter."}), 400

    return jsonify(sorted(
        POSTS,
        key=lambda p: p[sort_field].lower(),
        reverse=(direction == 'desc')
    ))


@app.route('/api/posts', methods=['POST'])
def post_posts():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400

    # Create ID for Post
    if POSTS:
        new_id = max(post["id"] for post in POSTS) + 1
    else:
        new_id = 1

    new_post = {
        "id": new_id,
        "title": title,
        "content": content
    }

    POSTS.append(new_post)
    return jsonify(new_post), 201


def find_post_by_id(post_id):
  """ Find the post with the id 'post_id'.
  If there is no post with this id, return None. """
  for post in POSTS:
    if post["id"] == post_id:
      return post
  return None


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_posts(id):
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"message": f"Post with id {id} not found."}), 404

    # Remove the post
    POSTS.remove(post)

    # Successful answer
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_posts(id):
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        return jsonify({"message": f"Post with id {id} not found."}), 404

    data = request.get_json()
    new_title = data.get('title', post['title'])
    new_content = data.get('content', post['content'])

    # Updating the fields, that where changed
    post['title'] = new_title
    post['content'] = new_content

    # Successful answer
    return jsonify({"id": id, "title": new_title, "content": new_content}), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    # Query-Parameter
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    # If neither title nor content parameters are specified return empty list
    if not title_query and not content_query:
        return jsonify([])

    # Filtering posts, that includes query parameter
    results = []
    for post in POSTS:
        matches_title = title_query and title_query in post['title'].lower()
        matches_content = content_query and content_query in post['content'].lower()

        # Append only, if at least one condition is met
        if matches_title or matches_content:
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
