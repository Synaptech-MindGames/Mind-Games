# Game plan

Pico park!!

First things first, we need to investigate (with loving support from ai) and how to connect our BCI's to the GUI. I heard from the other team that LSL could and should work! But there's much better open source repos they were ripping from. 

Also we need to figure out the game engine
There will be three modes, BCI mode, WASD/space mode, and hand tracking mode

You will be able to connect up to 4 BCI's into one device in order to play the game. It'll also need to be able to be played over the same network?

So

## Libraries

Language - Rust
Engine - Bevy 0.20.1
2D physics - Avian2D 0.8	
LAN multiplayer - Lightyear 0.31	
Networked physics - lightyear_avian2d 0.31	
Input management - Leafwing Input Manager 0.22	
Launcher communication - TCP + rmp-serde	
Serialization - Serde	
Game UI - Bevy UI	
Audio - Bevy Audio	
Testing - cargo test + Proptest

## Goals

1. Investigate whether LSL or another project would be the best way to wirelessly stream from the BCI's

2. Investigate open source recreations of Pico park, and if none exist, gotta get to creating one.
    I am completely down for making everything in Rust (Helps AI catch bugs and create programs that actually run) and specifically choosing libraries in Rust that will help to minimize ai slop.

3. Confirm it'll work on all OS's.

5. Will connect through LAN hosting (Local Area Network hosting), specifically direct client-server networking over a private IPv4 network

6. 2D game. Use github.com/Vanndavid/picopark-online as a reference when recreating in rust + bevy

7. Request data samples
    1. Clench left hand and hold. plus sporadic hand clenches
    2. Clench right hand and hold plus sporadic hand clenches
    3. Blink for jump