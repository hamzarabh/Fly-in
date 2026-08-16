***This project has been created as part of the 42 curriculum by hrabh.***

## Description
Design and implement an efficient drone routing system that coordinates multiple autonomous drones from a central base to target locations through a dynamic network, while optimizing their routes and managing resource constraints.


## Instructions

### Installation

```bash
make install
```
### Running
```bash
make run
```
### Debugging
```bash
make debug
```
### Linting
```bash
make lint
```

### Output format
Each line represents one simulation turn. Each drone movement is represented by D<ID>-<zone>. Drones that do not move during a turn are omitted.

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

## Parsing

The system parses a configuration file that defines the map structure, including zones, the number of drones, and connections between zones.
The configuration file is parsed using the Lark parsing library and transformed into structured data used by the routing system.
```
# Easy Level 3: Basic capacity management
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: bottleneck 1 0 [color=orange max_drones=2]
hub: wide_area 2 0 [color=blue max_drones=3]
end_hub: goal 3 0 [color=red]

connection: start-bottleneck [max_link_capacity=4]
connection: bottleneck-wide_area [max_link_capacity=4]
connection: wide_area-goal [max_link_capacity=4]
```

## Algorithm

The routing system combines Dijkstra's algorithm with Yen's K-shortest paths algorithm to find the two best routes between the source and target zones.
The resulting paths are assigned to the drones, allowing multiple drones to reach the target through different routes while optimizing path selection.

## Visual Representation

The system uses Pygame to provide a visual representation of the drone routing process, displaying the map, zones, connections, and drone movements.
The routing results are also displayed in the terminal, providing additional information about the selected paths and drone routes.

## Resources

- **Lark** — Parser / Grammar
  - https://lark-parser.readthedocs.io/_/downloads/en/latest/pdf/

- **Dijkstra** — Shortest Path Algorithm
  - https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php

- **Pygame** — Visualization
  - https://www.pygame.org/docs/

## AI usage
AI was used to research and understand the algorithms used in the project, learn the Pygame and Lark libraries, and assist with debugging by identifying errors and suggesting fixes. AI was also used to help generate and improve docstrings throughout the codebase.
