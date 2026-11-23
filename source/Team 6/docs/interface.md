# Game plan

so obviously we are competing against the other teams and must therefore create the best architecture and 'interface' to both play mindball, and other minigames we add later.

We originally decided with Python as the language to use (it's extremely easy to use) and we are gonna stick with it. I am thinking using it as the language for the interface, with the games themselves being modular. That way we can have them be standalone if need be so AI can iteratively test them, and not just restart the interface everytime. (we can also include a CLI for the ai's to run the modular minigames, or add 'doctor' commands)

And the interface should be able to run minigames made in python and rust for now, with other adaptors potentially added later

1. Do market research and see if there are existing open source interfaces that we can look at for the best architecture

2. Find the best streaming thing (If there's a better alternative than LSL)
