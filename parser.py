from lark import Lark, Transformer
from lark import UnexpectedInput, UnexpectedToken, UnexpectedEOF
from lark.exceptions import VisitError


class LogicError(Exception):
    pass


class SmartTransformer(Transformer):
    def __init__(self):
        self.color = False
        self.zone = False
        self.max_drones = False
        self.max_link_capacity = False
    def INT(self, token):
        return int(token)

    def SIGNED_INT(self, token):
        return int(token)

    def ZONE_NAME(self, token):
        return str(token).strip()

    def WORD(self, token):
        return str(token)

    def HUB(self, token):
        return str(token)

    def ZONE(self, token):
        if self.zone is True:
            raise UnexpectedInput(f"Duplicate zone property")
        else:
            self.zone = True
        return str(token)

    def COLOR(self, token):
        if self.color is True:
            raise UnexpectedInput(f"Duplicate color property")
        else:
            self.color = True
        return str(token)

    def con_meta(self, items):
        return int(items[0])

    def n_drone(self, items):
        if (items[0] <= 0):
            raise UnexpectedInput(
                "nb_drones cannot be less than or equal to 0")
        return {"type": "nb_drones", "nb": items[0]}

    def attr_color(self, items):
        return ("color", items[0])

    def attr_maxdron(self, items):
        if self.max_drones is True:
            raise UnexpectedInput(f"Duplicate max_drones property")
        else:
            self.max_drones = True
        if (items[0] <= 0):
            raise UnexpectedInput(
                "max_drones cannot be less than or equal to 0")
        return ("max_drones", items[0])

    def attr_zone(self, items):
        return ("zone", items[0])

    def attr_hub(self, items):
        return {
            "type": items[0],
            "name": items[1],
            "x": items[2],
            "y": items[3],
        }

    def at_meta(self, items):
        meta = {}
        for item in items[4:]:
            meta[item[0]] = item[1]
        if meta.get("zone"):
            if (meta["zone"] == "blocked"
                and items[0] in ("start_hub", "end_hub")):
                    raise UnexpectedInput(f"{items[0]} "
                                          "cannot be blocked")
        return {
            "type": items[0],
            "name": items[1],
            "x": items[2],
            "y": items[3],
            "meta": meta
        }

    def at_con(self, items):
        return {
            "type": "conection",
            "zone1": items[0],
            "zone2": items[1]
        }

    def at_con_meta(self, items):
        if self.max_link_capacity is True:
            raise UnexpectedInput(f"Duplicate max_link_capacity"
                                  " property")
        else:
            self.max_link_capacity = True
        return {
            "type": "conection",
            "zone1": items[0],
            "zone2": items[1],
            "max_link_capacity": items[2]
        }

    def __default__(self, name, children, meta):
        children = [c for c in children if c is not None and c != ""]
        if len(children) == 0:
            return None
        elif len(children) == 1:
            return children[0]
        else:
            return {
                "type": name,
                "data": children
            }


def syntax_parser(file):
    grammar = """
    start: seting+
    seting: "nb_drones" ":" INT -> n_drone
    | HUB ":" ZONE_NAME SIGNED_INT SIGNED_INT -> attr_hub
    | HUB ":" ZONE_NAME SIGNED_INT SIGNED_INT "[" attribute+ "]" -> at_meta
    | "connection" ":" ZONE_NAME "-" ZONE_NAME -> at_con
    | "connection" ":" ZONE_NAME "-" ZONE_NAME "[" conne_meta "]" ->at_con_meta
    | NEWLINE
    conne_meta: "max_link_capacity" "=" INT -> con_meta
    ZONE_NAME: /[^- ]+/
    HUB: "start_hub" | "end_hub" | "hub"
    attribute: "color" "=" WORD -> attr_color
    | "max_drones" "=" INT -> attr_maxdron
    | "zone" "=" ZONE      -> attr_zone
    ZONE: "normal" | "restricted" | "blocked" | "priority"

    %import common.NEWLINE
    %import common.INT
    %import common.SIGNED_INT
    %import common.WORD
    %import common.WS
    %import common.SH_COMMENT
    %ignore SH_COMMENT
    %ignore WS
    """
    parser = Lark(grammar, start="start", parser="lalr")
    res = []
    try:
        with open(file, "r") as file:
            nb_line = 1
            zone_names = []
            coordinates = []
            start = None
            end = None
            nb_drones = None
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    nb_line += 1
                    continue
                tree = parser.parse(line)
                data = SmartTransformer().transform(tree)
                if data:
                    if nb_drones:
                        if data["type"] == "nb_drones":
                            raise LogicError("Duplicate nb_drones")
                    else:
                        if data["type"] == "nb_drones":
                            nb_drones = data["type"]
                        else:
                            raise LogicError("nb_drones isn't the first")
                    if data["type"] in ["hub", "start_hub", "end_hub"]:
                        if data["name"] not in zone_names:
                            zone_names.append(data["name"])
                        else:
                            raise LogicError(
                                "The name of the zone is a duplicate")
                        if (data["x"], data["y"]) not in coordinates:
                            coordinates.append((data["x"], data["y"]))
                        else:
                            raise LogicError("Duplicate coordinates")
                        if data["type"] == "start_hub":
                            if start is None:
                                start = data["type"]
                            else:
                                raise LogicError(
                                    "`start_hub` must be defined only once")
                        if data["type"] == "end_hub":
                            if end is None:
                                end = data["type"]
                            else:
                                raise LogicError(
                                    "`end_hub` must be defined only once")
                    if data["type"] == "conection":
                        if (not data["zone1"] in zone_names):
                                raise LogicError(f"the zone '{data['zone1']}'"
                                                     " not defined")
                        if (not data["zone2"] in zone_names):
                            raise LogicError(f"the zone '{data['zone2']}'"
                                                    " not defined")
                        for item in res:
                            if (item["type"] == "conection"):
                                if item["zone1"] == item["zone2"]:
                                    raise LogicError("the zone cannot "
                                                     "connect to itself")
                                if ((item["zone1"] == data["zone1"]
                                    and item["zone2"] == data["zone2"])
                                    or  (item["zone1"] == data["zone2"]
                                    and item["zone2"] == data["zone1"])):
                                    raise LogicError("Connection to the two zones (duplicate)")
                    res.append(data)
                nb_line += 1
    except UnexpectedEOF:
        print(f"Error: the line is incomplete !, at line  {nb_line}\n")
        print("", line)
        print(f"	{' ' * (len(line) - 1)} ^")
        exit(1)
    except UnexpectedToken as e:
        e.line = nb_line
        print("Error:", e)
        print("` ,",line,"`")
        print(f"{' ' * (e.column - 1)} ^")
        exit(1)
    except UnexpectedInput as e:
        e.line = nb_line
        print(e)
        exit(1)
    except VisitError as e:
        print(e,f", at line {nb_line}")
        print("`",line,"`")
        exit(1)
    except LogicError as e:
        print("Error:", e, ", at line", nb_line)
        print("`",line,"`")
        exit(1)
    except (FileNotFoundError , PermissionError ) as e :
        print("Error: ",e)
        exit(1)

    if start is None:
        print("Error: The start zone is not defined !")
        exit(1)
    if end is None:
        print("Error: The end zone is not defined !")
        exit(1)
    return (res)


data = syntax_parser("config.txt")
# print(data)
