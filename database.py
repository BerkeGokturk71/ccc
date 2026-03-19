# Canlı hareketlerin tutulduğu liste
live_moves = []

def update_moves(new_data):
    global live_moves
    live_moves = new_data

def get_moves():
    return live_moves