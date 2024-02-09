# import redis
# import json
# import plotly.express as px

# fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
# # fig.show()

# Var = ["Geeks", "for", "Geeks"]

# r = redis.Redis()
# r.mset({"Croatia": Var, "Bahamas": "Nassau"})

# print(r.get('Croatia'))

from rejson import Client, Path

rj = Client(host='localhost', port=6379, decode_responses=True)

# Set the key `obj` to some object
obj = {
    'answer': 42,
    'arr': [None, True, 3.14],
    'truth': {
        'coord': 'out there'
    }
}
rj.jsonset('obj', Path.rootPath(), obj)

# Get something
print ('Is there anybody... {}?'.format(
    rj.jsonget('obj', Path('.truth.coord'))
))