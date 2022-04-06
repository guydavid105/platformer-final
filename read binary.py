import pickle

f = open("score_data", "rb")     # picks which level to read
data = f.read()
data2 = pickle.loads(data)
print(data2)                      # outputs the array

