import re
import pathlib

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

varDef = re.compile("(\S+)\s*=\s*(\S+)")
varUsage = re.compile(":\s*([\"\']\{(\S+)\}[\"\'])\s*;\s*$")

startDefBlock = re.compile("/\*\*\s*\{variables\}", flags=re.IGNORECASE)  # @UndefinedVariable


def varredCss2Css(varredCssIter):
    """
        Replaces a set of variables from an initial definitions commend block in the css
        settings.
        
        :param varredCssIter: a sequence of varred css lines
        :return: a generator over de-varred pure css lines
    """
    variables = {}
        
    inDefBlock = False
    for lNo, rawLine in enumerate(varredCssIter):
        line = rawLine.strip()

        if inDefBlock:
            if len(line) == 0 or line.startswith('#'):
                pass
            elif line.startswith('*/'):
                inDefBlock = False
            else:
                varMatch = varDef.match(line)
                if not varMatch:
                    raise ValueError("Could not find definition in line {}: {}".format(lNo + 1, line))
                variables[varMatch.group(1)] = varMatch.group(2)        
        elif startDefBlock.match(line):
            inDefBlock = True
        else:
            # not in definition block
            varOcc = varUsage.search(rawLine)
            if varOcc:
                varName = varOcc.group(2)
                varVal = variables.get(varName, None)
                if not varVal:
                    raise ValueError("Unknown variable '{}' in line {}: {}".format(varName, lNo + 1, line))
                yield rawLine.replace(varOcc.group(1), varVal)
                continue

        yield rawLine


if __name__ == '__main__':
    cssTmplPath = (pathlib.Path(__file__).parent / "../../resources/stylesheet.vars.css").resolve()
    print(cssTmplPath)
    with cssTmplPath.open() as cssIn:
        cssLines = cssIn.readlines()
    for l in varredCss2Css(cssLines):
        print(l)
