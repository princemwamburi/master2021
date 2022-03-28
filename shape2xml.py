# Input polygon shapefile converted from TIN surface
# tin_shp = r'C:\KnickKnackCivil\scripts\ExampleData\TinTriangles.shp'
import sys
import os
import shapefile
import lxml.etree as ET

def convert_to_landxml(tin_shp, unit_len,file_name):
    # Outputs
    out_xml = 'static/out/' + f'{file_name}_Surface.xml'
    # surf_name = os.path.splitext(os.path.basename(tin_shp))[0]
    surf_name = os.path.splitext(os.path.basename(tin_shp))[0]

    # Reading input TIN shapefile using PyShp
    in_shp = shapefile.Reader(tin_shp)
    shapeRecs = in_shp.shapeRecords()

    # Initializing landxml surface items
    namespace = {'xsi': "http://www.w3.org/2001/XMLSchema"}
    landxml = ET.Element('LandXML',
                         nsmap=namespace,
                         xmlns="http://www.landxml.org/schema/LandXML-1.2",
                         language='English',
                         readOnly='false',
                         time='08:00:00',
                         date='2019-01-01',
                         version="1.2")
    units = ET.SubElement(landxml, 'Units')
    surfaces = ET.SubElement(landxml, 'Surfaces')
    surface = ET.SubElement(surfaces, 'Surface', name=surf_name)
    definition = ET.SubElement(surface, 'Definition',
                               surfType="TIN")
    pnts = ET.SubElement(definition, 'Pnts')
    faces = ET.SubElement(definition, 'Faces')

    # Dictionary to define correct units based on input
    unit_opt = {'ft': ('Imperial', 'squareFoot', 'USSurveyFoot',
                       'cubicFeet', 'fahrenheit', 'inHG'),
                'm': ('Metric', 'squareMeter', 'meter',
                      'cubicMeter', 'celsius', 'mmHG'),
                'ft-int': ('Imperial', 'squareFoot', 'foot',
                           'cubicFeet', 'fahrenheit', 'inHG')}

    # Define units here. Has not been tested with metric.
    unit = ET.SubElement(units,
                         unit_opt[unit_len][0],
                         areaUnit=unit_opt[unit_len][1],
                         linearUnit=unit_opt[unit_len][2],
                         volumeUnit=unit_opt[unit_len][3],
                         temperatureUnit=unit_opt[unit_len][4],
                         pressureUnit=unit_opt[unit_len][5])

    # Initializing output variables
    pnt_dict = {}
    face_list = []
    cnt = 0

    print('Processing...')

    # Creating reference point dictionary/id for each coordinate
    # As well as LandXML points, and list of faces
    for sr in shapeRecs:
        shape_pnt_ids = []  # id of each shape point

        # Each shape should only have 3 points
        for pnt in range(3):
            # Coordinate with y, x, z format
            coord = (sr.shape.points[pnt][1],
                     sr.shape.points[pnt][0],
                     # sr.shape.z[pnt]
                     )

            # If element is new, add to dictionary and
            # write xml point element
            if coord not in pnt_dict:
                cnt += 1
                pnt_dict[coord] = cnt

                shape_pnt_ids.append(cnt)  # Add point id to list

                # Individual point landxml features
                # pnt_text = f'{coord[0]:.5f} {coord[1]:.5f} {coord[2]:.3f}'
                pnt_text = f'{coord[0]:.5f} {coord[1]:.5f}'
                pnt = ET.SubElement(pnts, 'P', id=str(cnt)).text = pnt_text

            # If point is already in the point dictionary, append existing point id
            else:
                shape_pnt_ids.append(pnt_dict[coord])

        # Check if too many or too few points created
        if len(shape_pnt_ids) != 3:
            print('Error - check input shapefile. ' \
                  'Must be a polygon with only three nodes for each shape.')
            sys.exit(0)

        # Reference face list for each shape
        face_list.append(shape_pnt_ids)

    # Writing faces to landxml
    for face in face_list:
        ET.SubElement(faces, 'F').text = f'{face[0]} {face[1]} {face[2]}'

    # Writing output
    tree = ET.ElementTree(landxml)
    tree.write(out_xml, pretty_print=True, xml_declaration=True, encoding="iso-8859-1")
    print(f'Successfully created {out_xml}. Check file output.')
    return out_xml
