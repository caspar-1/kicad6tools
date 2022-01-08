import kicad6tools.eeschema as k6



if __name__ == "__main__":
    sch_file = "../../kicad/test/test_hier_orig.kicad_sch"
    with open(sch_file, "r") as fh:
        sexp = str(fh.read())

    eeschema = k6.Schematic(sexp)
    sexpr = eeschema.generate_schematic_sexpr()

    with open("../../kicad/test/test.kicad_sch", "w") as fh:
        fh.write(sexpr)
    with open("bad.kicad_sch", "w") as fh:
        fh.write(sexpr)