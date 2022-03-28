import os.path
import shlex
import subprocess


class ConvertGml():
    def __init__(self):
        if os.name == 'nt':
            self.ogr2ogr_path = "C:\Program Files\GDAL\ogr2ogr.exe"
        else:
            self.ogr2ogr_path = "ogr2ogr"

    def convert_shp(self, filename,out_folder):
        input = os.path.join(os.getcwd(),"static","input", filename + ".shp")
        output = os.path.join(os.getcwd(),"static","out",out_folder, filename + ".gml")
        cmd = f'{self.ogr2ogr_path} -f "GML" {output} {input}'
        out_cns = subprocess.run(cmd)
        print(out_cns)
        return output
