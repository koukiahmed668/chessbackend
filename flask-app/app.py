import numpy as np
import tensorflow as tf
from tensorflow import keras
import chess
import chess.pgn
from flask import Flask, request, jsonify

# Function to parse PGN file and load games
def parse_pgn(file_path):
    with open(file_path, 'r') as pgn_file:
        games = []
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            games.append(game)
    return games

# Function to extract features and labels from games
def extract_features_and_labels(games):
    X = []
    y = []
    for game in games:
        board = game.board()
        for move in game.mainline_moves():
            X.append(board_to_features(board))
            y.append(move_to_index(move))
            board.push(move)
    return np.array(X), np.array(y)

# Function to convert a board to input features
def board_to_features(board):
    features = np.zeros((64, 12), dtype=np.float32)
    piece_map = board.piece_map()
    for square, piece in piece_map.items():
        piece_type = piece.piece_type - 1  # piece_type is 1-6, make it 0-5
        color_offset = 6 if piece.color == chess.BLACK else 0
        features[square][piece_type + color_offset] = 1
    return features.flatten()

# Function to convert a move to an index
def move_to_index(move):
    return move.from_square * 64 + move.to_square

games = parse_pgn('Adams.pgn')  # Update with the correct path

X, y = extract_features_and_labels(games)

y = keras.utils.to_categorical(y, num_classes=4096)
# Build a simple model
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(768,)),  # Updated input shape
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(4096, activation='softmax')
])
# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Reshape X to fit the model
X = X.reshape((-1, 768))

# Train the model
model.fit(X, y, epochs=1, batch_size=64, validation_split=0.1)

# Save the model
model.save("chess_model.h5")

model = keras.models.load_model("chess_model.h5")


# Predict the next move
def predict_move(board):
    features = board_to_features(board).reshape(1, 768)  # Reshape to match model input shape
    prediction = model.predict(features)
    
    move_index = np.argmax(prediction)
    from_square = move_index // 64
    to_square = move_index % 64
    
    move = chess.Move(from_square, to_square)
    
    if move in board.legal_moves:
        return move
    else:
        return list(board.legal_moves)[0]

app = Flask(__name__)

# Flask route to handle move prediction
@app.route('/predict_move', methods=['POST'])
def handle_predict_move():
    data = request.json
    fen = data.get('fen')
    
    if not fen:
        return jsonify({"error": "FEN string is required"}), 400
    
    board = chess.Board(fen)
    move = predict_move(board)
    
    return jsonify({"move": move.uci()})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
