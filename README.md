# The Terminal

An entry into the Github 2016 Game-Off game jam, this is a cooperative hacking
game in the style of [Keep Talking and Nobody Explodes](http://keeptalkinggame.com).

## Setup
* Install python3 and the pygame module.
* Clone the repository: git clone https://github.com/juzley/game-off-2016
* Change into the directory containing the repository.
* Generate the manual image for the decryption puzzle: python3 -m tools.decrypt_image
* Launch the game: python3 ggo16.py
* The manual is in the manual directory.

## How to play
The aim of the game is to complete a series of 'hacking' challenges to gain
access to a system. This is a cooperative game: one player sits at the terminal
and interacts with it, one or more other players guide this player through the
puzzles based on the contents of the hacking manual. It is important that the
player at the terminal cannot see the manual, and the other players cannot see
the terminal!


