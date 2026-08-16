from parser import syntax_parser
from zone import create_zones
from visualizer import loop, Drone, Visualizer


def main() -> None:
    """Create the drones, and start the simulation."""
    data = syntax_parser("maps/linear_path.txt")
    nb_drons = data[0]['nb']
    zones = create_zones(data)
    for z in zones.values():
        if z.type == "start_hub":
            start = z
        if z.type == "end_hub":
            end = z

    drones = []

    for i in range(nb_drons):
        drone = Drone(
            f"D{i+1}",
            zones,
            start,
            end
        )
        result = drone.FindPath()
        if i == 0 and result is False:
            print("Error: not path in this grafe")
            exit(1)

        drones.append(drone)
    v1 = Visualizer(zones, drones)
    loop(v1)
    return None


if __name__ == "__main__":
    main()
