from tkinter import *
import pickle


def leader():
    g = open("score_data", "rb")  # picks which level to read
    data3 = g.read()
    leaderboard_data = pickle.loads(data3)
    g.close()
    leaderboard_data.remove(leaderboard_data[0])
    leaderboard_data = sorted(leaderboard_data, key=lambda x: x[1])
    leaderboard_data.reverse()

    root = Tk()
    scrollbar = Scrollbar(root)
    scrollbar.pack(side=RIGHT, fill=Y)

    my_list = Listbox(root, yscrollcommand=scrollbar.set)
    for i in leaderboard_data:
        my_list.insert(END, str(i))

    my_list.pack(side=LEFT, fill=BOTH)
    scrollbar.config(command=my_list.yview)

    Button(root, text="Quit", command=root.destroy).pack()

    mainloop()
