# Game plan

so obviously we are competing against the other teams and must therefore create the best architecture and 'interface' to both play mindball, and other minigames we add later.

We originally decided with Python as the language to use (it's extremely easy to use) and we are gonna stick with it. I am thinking using it as the language for the interface, with the games themselves being modular. That way we can have them be standalone if need be so AI can iteratively test them, and not just restart the interface everytime. (we can also include a CLI for the ai's to run the modular minigames, or add 'doctor' commands)

And the interface should be able to launch minigames made in python and rust for now, with other adaptors potentially added later

This interface is also going to be how the EEGs connect connect to the games. It'll basically take the ifno from the BCI's, and then feed it into the games themselves. It will use the brainflow library for this

- EEG Data - Brainflow
- Language - Python 3.13
- Graphical Framework - PySide6
- UI - Qt Quick / QML
- Numerical Processing - NumPy
- Signal Processing - BrainFlow DataFilter + SciPy
- Launcher-to-game - TCP + MessagePack
- Game launching - QProcess
- Database - SQLite (built-in sqlite3)
- CLI for AI - Typer
- EEG Graphs - Qt Graphs
- Testing - ruff + pytest
- Deployment - pyside6-deploy

1. Do market research and see if there are existing open source interfaces that we can look at for the best architecture

2. Find the best streaming thing (If there's a better alternative than LSL)
