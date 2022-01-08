from os import read
import re

dict = {
    "Applied_poison_rating_bonus": (
        lambda target, magnitude: target.equipmentPoisonRatingBonus + magnitude
    )
}


class base:
    def __init__(self, v):
        self.v = v

    def init(self, keys, data):
        for idx in range(len(data)):
            c = data[idx]
            isValPair = False
            if isinstance(c, list):
                k = c[0]
            else:
                k = c
                isValPair = True
            print(k)
            f = keys.get(k, None)
            if f:
                if isValPair:
                    f(self, data[idx + 1])
                else:
                    f(self, c[1:])

    def as_sexpr(self, d, level=0):
        s = ""
        quote = False
        if d is not None:
            for c in d:
                quote_next = False
                if isinstance(c, list):
                    s += "({})\n".format(self.as_sexpr(c, -1))

                else:
                    if isinstance(c, str):
                        if (" " in c) or ("~" in c) or ("-" in c) or (":" in c):
                            c = '"{}"'.format(c)
                        if c == "number":
                            quote_next = True

                    if len(str(c)) == 0:
                        c = '""'
                    if quote == True:
                        s += '"{}" '.format(c)

                    else:
                        s += "{} ".format(c)

                    quote = quote_next

        return s

    def generate_sexpr(self):
        s = self.as_sexpr(self.v) + "\n"
        return s


class uniterpreted_obj(base):
    def __init__(self, v):
        super().__init__(v)


class lib_symbols(base):
    def __init__(self, v):
        super().__init__(v)

    def generate_sexpr(self):
        s = "(lib_symbols\n {})\n".format(self.as_sexpr(self.v))
        return s


class wire(base):
    def __init__(self, v):
        super().__init__(v)

    def generate_sexpr(self):
        s = "(wire\n {})\n".format(self.as_sexpr(self.v))
        return s


class junction(base):
    def __init__(self, v):
        super().__init__(v)

    def generate_sexpr(self):
        s = "(junction\n {})\n".format(self.as_sexpr(self.v))
        return s

class symbol_instances(base):
    def __init__(self, v):
        super().__init__(v)

    def generate_sexpr(self):
        s = "(symbol_instances\n {})\n".format(self.as_sexpr(self.v))
        return s

class sheet(base):
    def __init__(self, v):
        super().__init__(v)

    def generate_sexpr(self):
        s = "(sheet\n {})\n".format(self.as_sexpr(self.v))
        return s


class sheet_instance(base):
    keys = {
        "path": (lambda target, v: setattr(target, "path", v)),
        "page": (lambda target, v: setattr(target, "page", v[0])),
    }
    def __init__(self, v):
        super().__init__(v)
        self.path = None
        self.page = None
        self.init(sheet_instance.keys,v)
        pass

    def generate_sexpr(self):
        s = "(path \"{}\"(page \"{}\"))".format(self.path,self.page)
        return s


class sheet_instances(base):
    
    def __init__(self, v):
        super().__init__(v)
        self.sheets=[]
        for  s in v:
            self.sheets.append(sheet_instance(s))
        pass

    def generate_sexpr(self):
        s = "(sheet_instances\n"
        s+= "\n".join([s.generate_sexpr() for s in self.sheets])
        s+= "\n)\n"
        return s


class Property(base):
    keys = {
        "id": (lambda target, v: setattr(target, "id", v[0])),
        "at": (lambda target, v: setattr(target, "at", v)),
        "effects": (lambda target, v: setattr(target, "effects", v)),
        "hide": (lambda target, v: setattr(target, "visability", "hide")),
        "show": (lambda target, v: setattr(target, "visability", "show")),
    }

    def __init__(self, v):
        super().__init__(v)

        self.Property = v[0]
        self.value = v[1]
        self.id = None
        self.at = None
        self.effects = None
        self.visability = ""
        self.init(Property.keys, v)
        pass

    def generate_sexpr(self):
        s = "(property \"{}\" ".format(self.Property)
        s += "\"{}\" ".format(self.value)
        s+= "(id {}) ".format(self.id) 
        s+="(at {})".format(" ".join([str(v) for v in self.at]))
        s+= "(effects {}) ".format(self.as_sexpr(self.effects))
        s+= "{} ".format(self.visability) 
        s+=")\n"
         

        return s


class pin(base):
    keys = {
        "uuid": (lambda target, v: setattr(target, "uuid", v[0])),
        
    }

    def __init__(self, v):
        super().__init__(v)

        self.pin = v[0]
        self.uuid = None
        self.init(pin.keys, v)
        pass

    def generate_sexpr(self):
        s = "(pin \"{}\" ".format(self.pin)
        s += "(uuid {})".format(self.uuid)
        s += ")\n"
        return s
        


class Symbol(base):

    keys = {
        "lib_id": lambda target, v: setattr(target, "lib_id",["lib_id",v[0]]),
        "at": (lambda target, v: setattr(target, "at", v)),
        "unit": (lambda target, v: setattr(target, "unit",v[0])),
        "in_bom": (lambda target, v: setattr(target, "in_bom", v[0])),
        "on_board": (lambda target, v: setattr(target, "on_board", v[0])),
        "uuid": (lambda target, v: setattr(target, "uuid", v[0])),
        "property": (lambda target, v: target.property.append(Property(v))),
        "pin": (lambda target, v: target.pin.append(pin(v))),
    }

    def __init__(self, v):
        super().__init__(v)
        self.lib_id = None
        self.at = None
        self.unit = None
        self.in_bom = None
        self.on_board = None
        self.uuid = None
        self.property = []
        self.pin = []

        self.init(Symbol.keys, v)
        pass

    def generate_sexpr(self):
        s = "(symbol\n"
        s+=self.as_sexpr([self.lib_id])
        s+="(at {})".format(" ".join([str(v) for v in self.at]))
        s+="(unit {})".format(self.unit)
        s+="(in_bom {})".format(self.in_bom)
        s+="(on_board {})".format(self.on_board)
        s+="(uuid {})".format(self.uuid)
        s+="\n".join([p.generate_sexpr() for p in self.property])
        s+="\n".join([p.generate_sexpr() for p in self.pin])
        s+=")\n"
        return s


class Schematic(base):
    term_regex = r"""(?mx)
        \s*(?:
            (?P<brackl>\()|
            (?P<brackr>\))|
            (?P<uuid>\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)|
            (?P<num>\-?\d+\.\d+|\-?\d+)|
            (?P<sq>"[^"]*")|
            (?P<s>[^(^)\s]+)
        )"""

    keys = {
        "version": lambda target, v: setattr(target, "version", v[0]),
        "generator": (lambda target, v: setattr(target, "generator", v[0])),
        "eeschema": (lambda target, v: setattr(target, "eeschema", v[0])),
        "uuid": (lambda target, v: setattr(target, "uuid", v[0])),
        "paper": (lambda target, v: setattr(target, "paper", v[0])),
        "lib_symbols": (
            lambda target, v: setattr(target, "lib_symbols", lib_symbols(v))
        ),
        "junction": (lambda target, v: target.junction.append(junction(v))),
        "wire": (lambda target, v: target.wire.append(wire(v))),
        "symbol": (lambda target, v: target.symbol.append(Symbol(v))),
        "sheet": (lambda target, v: target.sheet.append(sheet(v))),
        "sheet_instances": (
            lambda target, v: setattr(target, "sheet_instances", sheet_instances(v))
        ),
        "symbol_instances": (
            lambda target, v: setattr(target, "symbol_instances", symbol_instances(v))
        ),
    }

    def __init__(self, s):

        self.version = None
        self.generator = None
        self.eeschema = None
        self.paper = None
        self.uuid = None
        self.lib_symbols = None
        self.junction = []
        self.wire = []
        self.symbol = []
        self.sheet = []
        self.sheet_instances = None
        self.symbol_instances = None

        f = self.parse_sexp(s)
        self.init(Schematic.keys, f)
        pass

    def parse_sexp(self, sexp):
        self.dbg = False
        stack = []
        out = []
        if self.dbg:
            print("%-6s %-14s %-44s %-s" % tuple("term value out stack".split()))
        for termtypes in re.finditer(Schematic.term_regex, sexp):
            term, value = [(t, v) for t, v in termtypes.groupdict().items() if v][0]
            if self.dbg:
                print("%-7s %-14s %-44r %-r" % (term, value, out, stack))
            if term == "brackl":
                stack.append(out)
                out = []
            elif term == "brackr":
                assert stack, "Trouble with nesting of brackets"
                tmpout, out = out, stack.pop(-1)
                out.append(tmpout)
            elif term == "num":
                v = float(value)
                if v.is_integer():
                    v = int(v)
                out.append(v)
            elif term == "sq":
                out.append(value[1:-1])
            elif term == "s":
                out.append(value)

            elif term == "uuid":
                out.append(value)
            else:
                raise NotImplementedError("Error: %r" % (term, value))
        assert not stack, "Trouble with nesting of brackets"
        return out[0]

    def generate_schematic_sexpr(self):
        sexpr = "("
        sexpr += (
            """kicad_sch (version {}) (generator {}) (uuid {}) (paper "{}")\n""".format(
                self.version, self.generator, self.uuid, self.paper
            )
        )
        sexpr += self.lib_symbols.generate_sexpr()
        sexpr += "".join([j.generate_sexpr() for j in self.junction])
        sexpr += "".join([j.generate_sexpr() for j in self.wire])
        sexpr += "".join([j.generate_sexpr() for j in self.symbol])
        sexpr += "".join([j.generate_sexpr() for j in self.sheet])
        sexpr += self.sheet_instances.generate_sexpr()
        sexpr += self.symbol_instances.generate_sexpr()
        sexpr += ")"
        return sexpr



