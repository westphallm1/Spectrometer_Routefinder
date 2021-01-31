import shapefile
import os

SHAPE_TYPES = {'Polygon': 5, 'Point': 1}
KEYS = 'lon', 'lat'


def findPointCoords(shpfile):
    shpf = shapefile.Reader(shpfile)
    coords = []
    for shape in shpf.shapes():
        if shape.shapeType == SHAPE_TYPES['Point']:
            coords.append(dict(zip(KEYS, shape.points[0])))
    return coords


def findPolyCoords(shpfile):
    shpf = shapefile.Reader(shpfile)
    coords = []
    for shape in shpf.shapes():
        if shape.shapeType == SHAPE_TYPES['Polygon']:
            coords += [[dict(zip(KEYS, p)) for p in shape.points]]
    return coords


def findRegionType(shpfile, types_to_check=("Polygon", "Point")):
    shpf = shapefile.Reader(shpfile)
    for shape in shpf.shapes():
        for t in types_to_check:
            if shape.shapeType == SHAPE_TYPES[t]:
                return t
    return None


def findMeta(shpfile):
    shpf = shapefile.Reader(shpfile)
    keys = [key[0] for key in shpf.fields[1:]]
    out = {key: [] for key in keys}
    for record in shpf.records():
        for idx, value in enumerate(record):
            out[keys[idx]].append(value)
    return out


def coordDictListToCoord2DList(coord_dict_list, alt=0):
    coords = list(map(lambda c: [c['lon'], c['lat'], alt], coord_dict_list))
    nested_coords = [[p1, p2] for p1, p2 in zip(coords[::2], coords[1::2])]
    return [coords]


def planOutlineFromCoords(fname, regions, alt, approach, bearing, sidelap,
                          inst, names, vehic='fullscale', units='US', starttrig=0.5, endtrig=0.5):
    polyw = shapefile.Writer(fname, shapeType=shapefile.POLYGON)
    polyw.field('name', 'C', 40)
    polyw.field('alt', 'F', 12)
    polyw.field('approach', 'F', 12)
    polyw.field('bearing', 'F', 12)
    polyw.field('sidelap', 'F', 12)
    polyw.field('inst', 'C', 40)
    polyw.field('frame', 'S', 6)
    polyw.field('fov', 'S', 8)
    polyw.field('ifov', 'S', 8)
    polyw.field('pixels', 'F', 10)
    polyw.field('vehicle', 'C', 20)
    polyw.field('units', 'C', 10)
    polyw.field('trigstart', 'F', 6, 2)
    polyw.field('trigend', 'F', 6, 2)
    for area, name in zip(regions, names):
        bounds = coordDictListToCoord2DList(area, 0)
        polyw.poly(bounds)
        #polyw.poly(parts=bounds)
        polyw.record(
            name,
            alt,
            approach,
            bearing,
            sidelap * 100,
            inst.name,
            inst.frame,
            inst.fieldOfView,
            inst.crossFieldOfView,
            inst.pixels,
            vehic,
            units,
            starttrig,
            endtrig
        )
    #polyw.save(fname)
    polyw.close()
#TODO: alt and speed do not seem to be used in writing shp files?
def flightPlanFromCoords(outpath, coords, scanlinebounds, alt, speed, trigcoords=None):
    if not os.path.isdir(outpath):
        os.makedirs(outpath)
    linew = shapefile.Writer(os.path.join(outpath, 'scanlines'), shapeType=shapefile.POLYLINEZ)
    linew.field('idx', 'N', 10)
    footw = shapefile.Writer(os.path.join(outpath, 'footprints'), shapeType=shapefile.POLYGONZ)
    footw.field('idx', 'N', 10)
    pointw = shapefile.Writer(os.path.join(outpath, 'points'), shapeType=shapefile.POINTZ)
    pointw.field('idx', 'N', 10)
    pointw.field('type', 'C', 40)

    trigpointsw = None
    triglinesw = None
    if trigcoords:
        trigpointsw = shapefile.Writer(os.path.join(outpath, 'trigger_points'), shapeType=shapefile.POINTZ)
        triglinesw = shapefile.Writer(os.path.join(outpath, 'trigger_lines'), shapeType=shapefile.POLYLINEZ)

        trigpointsw.field('idx', 'N', 10)
        trigpointsw.field('type', 'C', 40)

        triglinesw.field('idx', 'N', 10)

    for i in range(int(len(coords) / 4)):
        # write the scan area first
        bounds = coordDictListToCoord2DList(scanlinebounds[i], 0)
        #footw.poly(parts=bounds)
        footw.polyz(bounds)
        footw.record(str(i), 'Scanline Bounds')
        # then the flight line
        line = coordDictListToCoord2DList(coords[4 * i:4 * i + 4])
        #linew.poly(parts=line, shapeType=shapefile.POLYLINE)
        linew.linez(line)
        linew.record(i)
        # then the start/end/entry/exit points of the flight line
        pointw.pointz(*line[0][0])
        pointw.pointz(*line[0][1])
        pointw.pointz(*line[0][2])
        pointw.pointz(*line[0][3])
        [pointw.record(i, p) for p in ["START", "ENTER", "EXIT", "END"]]

        if trigcoords:
            trigline = coordDictListToCoord2DList(trigcoords[i])
            triglinesw.linez(trigline)
            triglinesw.record(i)

            trigpointsw.pointz(*trigline[0][0])
            trigpointsw.pointz(*trigline[0][1])
            for p in ["START","END"]:
                trigpointsw.record(i,p)

    linew.close()
    footw.close()
    pointw.close()
    if trigcoords:
        triglinesw.close()
        trigpointsw.close()