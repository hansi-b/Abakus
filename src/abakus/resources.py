import pathlib
import logging

__author__ = "Hans Bering"
__copyright__ = "Copyright 2019, Hans Bering"
__license__ = "GPL3"
__status__ = "Development"

__RESOURCES_ROOT = None


def path(resPath):
    global __RESOURCES_ROOT
    if __RESOURCES_ROOT is None:
        curr = pathlib.Path(__file__).parent
        for depth in (0, 2):
            __RESOURCES_ROOT = curr / "{}resources".format(depth * "../")
            if __RESOURCES_ROOT.is_dir():
                break
        else:
            raise AssertionError("Ressourcen konnten von '{}' aus nicht gefunden werden".format(curr))
        
    fullPath = (__RESOURCES_ROOT / resPath).resolve()
    if not fullPath.exists():
        logging.error("Ressource '{}' wurde nicht gefunden (gesucht in '{}')".format(resPath, fullPath))
    return str(fullPath)


def load(resPath, loaderFunc):
    with open(path(resPath), "r") as resF:
        return loaderFunc(resF)


if __name__ == '__main__':
    pass
