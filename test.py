from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

# Accessing REDIS_HOST from app config
redis_host = app.config['REDIS_HOST']

# Print the value to verify
print(redis_host)