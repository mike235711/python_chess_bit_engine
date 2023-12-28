# Neural-Network Chess-Engine [In progress]
In this project I will create a chess engine from scratch. Classical chess engines usually consist of 3 main parts:

* A move generator, generating all legal moves in a chess position
* A function that evaluates positions (Possibly a neural network)
* An algorithm that searches in the variations and chooses the best

I have created my own move generator, taking into account all the rules of chess and implementing an idea I had of making use of the symmetries of the chess board. Speed in this part of the engine is essential because the engine will have to calculate many variations and chess is usually played with time limtis. *Since python is not the fastest programming language in the future I will rewrite this in C++.*

When evaluating positions, my idea is to use a neural network. Since speed is very important we can't use any neural network to evaluate positions, there are a special type of nerual networks called efiiciently updatable neural networks (NNUE) which are fast enough for chess engines and can be trained to evaluate positions to a very high level.

There are many choices of search algorithms for chess engines, however alpha-beta pruning is the most efficient because it prunes branches of the tree search that one doesn't need to search. On top of the alpha beta search I have added a score to moves depending on capturing pieces, pawns and making checks. The algorithm is contructed such that it considers high score moves first, making it faster because it prunes more branches. I have also applied quiescence search so that in tactical positions (when there are possible captures or checks by either side) it moves reasonably until a quiet position is reached.

To do:
* Castling moves don't appear in gen_moves - fixed
* Hash Tables - Done (Speeds up to twice the Engine, see notebook)
* 50 move rule
* Iterative deepening - Done, but want to add variations not only first move
* Killer moves - Done (Can speed up engine up to 1.5 times as much, depending on position)
* Null move pruning
* NNUE (In progress)
* Connect to UCI (In progress)
