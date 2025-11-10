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
    return jsonify(POSTS)


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
  """ Find the post with the id `post_id`.
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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
