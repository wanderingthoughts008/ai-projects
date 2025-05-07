import chess
import random
import math


class ChessAI:
    def __init__(self, depth=4):
        self.depth = depth
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        self.piece_square_tables = {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, -20, -20, 10, 10, 5,
                5, -5, -10, 0, 0, -10, -5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, 5, 10, 25, 25, 10, 5, 5,
                10, 10, 20, 30, 30, 20, 10, 10,
                50, 50, 50, 50, 50, 50, 50, 50,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.KNIGHT: [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50
            ],
            chess.BISHOP: [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -10, -10, -10, -10, -10, -20
            ],
            chess.ROOK: [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, 10, 10, 10, 10, 5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                0, 0, 0, 5, 5, 0, 0, 0
            ],
            chess.QUEEN: [
                -20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -5, 0, 5, 5, 5, 5, 0, -5,
                0, 0, 5, 5, 5, 5, 0, -5,
                -10, 5, 5, 5, 5, 5, 0, -10,
                -10, 0, 5, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20
            ],
            chess.KING: [
                20, 30, 10, 0, 0, 10, 30, 20,
                20, 20, 0, 0, 0, 0, 20, 20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30
            ]
        }

    def evaluate_board(self, board):
        if board.is_checkmate():
            return -math.inf if board.turn else math.inf
        if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
            return 0

        score = 0
        for piece_type in self.piece_values:
            white_pieces = board.pieces(piece_type, chess.WHITE)
            black_pieces = board.pieces(piece_type, chess.BLACK)
            score += len(white_pieces) * self.piece_values[piece_type]
            score -= len(black_pieces) * self.piece_values[piece_type]

            # Piece-square tables
            pst = self.piece_square_tables[piece_type]
            for square in white_pieces:
                score += pst[square]
            for square in black_pieces:
                score -= pst[chess.square_mirror(square)]  # mirror for black

        score += self.evaluate_pawn_structure(board)
        score += self.evaluate_mobility(board)

        return score if board.turn == chess.WHITE else -score

    def evaluate_pawn_structure(self, board):
        score = 0
        for file in range(8):
            white_pawns = len(board.pieces(chess.PAWN, chess.WHITE) & chess.BB_FILES[file])
            black_pawns = len(board.pieces(chess.PAWN, chess.BLACK) & chess.BB_FILES[file])
            if white_pawns > 1:
                score -= 10 * (white_pawns - 1)
            if black_pawns > 1:
                score += 10 * (black_pawns - 1)
        return score if board.turn == chess.WHITE else -score

    def evaluate_mobility(self, board):
        mobility = board.legal_moves.count()
        return 0.1 * mobility if board.turn == chess.WHITE else -0.1 * mobility

    def alpha_beta_search(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if maximizing:
            max_eval = -math.inf
            for move in board.legal_moves:
                board.push(move)
                eval = self.alpha_beta_search(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval = self.alpha_beta_search(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self, board):
        best_move = None
        best_value = -math.inf if board.turn == chess.WHITE else math.inf

        for move in board.legal_moves:
            board.push(move)
            move_value = self.alpha_beta_search(board, self.depth - 1, -math.inf, math.inf, board.turn == chess.BLACK)
            board.pop()

            if board.turn == chess.WHITE and move_value > best_value:
                best_value = move_value
                best_move = move
            elif board.turn == chess.BLACK and move_value < best_value:
                best_value = move_value
                best_move = move

        if best_move is None:
            best_move = random.choice(list(board.legal_moves))

        return best_move
