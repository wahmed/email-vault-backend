import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from my_flask.app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
