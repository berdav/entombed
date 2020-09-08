# Entombed :maze:

Who wants to do a Rorschach test? :smile:
Maze generator based on the "misterious" Entombed algorithm.
![Example script execution](resources/tool.png)

## What is it?
This program could generate different mazes based on the cellular
automata found in Entombed Atari 2600 Game.

It could be used to explore different cellular automata generation for
the mazes.

## How can I use it?
To generate a maze simply execute the script:
![Simple maze](resources/maze.png)

The script has many configurations, such as disabling of symmetrical
generation with `-S`:
![Half maze](resources/halfmaze.png)

To get a list of configurations use the switch `-h` or `--help`

You can reconfigure the cellular automata rules using the parameter
`-R`.  You can refer to the help to get the usage of this parameter.
For example
```bash
$ ./entombed.py -R  -p
```
Generate the following rules
![Rules](resources/rules.png)

And mazes similar to this one
![Mazes with custom Rules](resources/maze_rule.png)

## Thanks
This work is based on the work
"Entombed: An archaeological examination of an Atari 2600 game" by
John Aycock1 and Tara Copplestone published in 
The Art, Science, and Engineering of Programming, 2019, Vol. 3, Issue 2, Article 4

You can find the work at ![arxiv](https://arxiv.org/pdf/1811.02035v1)