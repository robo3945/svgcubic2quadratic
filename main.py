import getopt
import os
import sys
from pathlib import Path
from xml.dom import minidom

import svgpathtools as svgpathtools
from colorama import Fore
from svgpathtools import QuadraticBezier, CubicBezier


def process_a_svg_file(file_object: Path) -> str:
    """
    prcess a single SVG file converting Cubic in Quadric curves
    :param file_object:
    :return:

    https://stackoverflow.com/questions/3162645/convert-a-quadratic-bezier-to-a-cubic-one

    """
    content = file_object.read_text()
    mydoc = minidom.parseString(content)
    path_tags = mydoc.getElementsByTagName("path")
    for p in path_tags:
        d_string = p.attributes['d'].value
        path_elements = svgpathtools.parse_path(d_string)
        new_path_elements = svgpathtools.Path()
        for p_element in path_elements:
            if isinstance(p_element, CubicBezier):
                c = p_element
                # c_control = 1.5 * c.control1 - 0.5 * c.start
                c_control = 1.5 * c.control2 - 0.5 * c.end
                q = QuadraticBezier(c.start, c_control, c.end)
                new_path_elements.append(q)
            else:
                new_path_elements.append(p_element)

        if new_path_elements:
            p.attributes['d'].value = new_path_elements.d()

        print(Fore.LIGHTYELLOW_EX + f"-" * 20 + Fore.RESET)
        print(Fore.LIGHTRED_EX + f"path_elements.d(): {path_elements.d()}" + Fore.RESET)
        print(Fore.LIGHTRED_EX + f"new_path_elements: {new_path_elements}" + Fore.RESET)
        print(Fore.LIGHTRED_EX + f"new_path_elements.d(): {new_path_elements.d()}" + Fore.RESET)
        print(Fore.LIGHTYELLOW_EX + f"-" * 20 + Fore.RESET)
        print()

    return str(mydoc.toxml())


def process_svg_files(inputdir: str, output_dir: str):
    i_dir = Path(inputdir)
    if i_dir.is_dir():
        with os.scandir(i_dir) as it:
            print(Fore.LIGHTGREEN_EX + f"+ dir: {i_dir.absolute()}" + Fore.RESET)
            for f in it:
                f1 = Path(f)
                if f1.is_file() and f1.suffix.lower() == ".svg":
                    print(Fore.LIGHTGREEN_EX + f"-> svg file: {f1.absolute()}" + Fore.RESET)
                    # exchange the curve degree
                    xml = process_a_svg_file(f1)

                    # write the new SVG file
                    o_file = Path(output_dir).joinpath(f1.name)
                    print(Fore.LIGHTGREEN_EX + f"-> written new svg file: {o_file.absolute()}" + Fore.RESET)
                    o_file.write_text(xml)


usage_sample = """

Directories scan: main.py -i <inputdir> -o <outdir> [-h]

-i <inputdir>       : the starting directory
-o <outputdir>       : the starting directory
"""

if __name__ == '__main__':

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:")
    except getopt.GetoptError as error:
        print('************ arguments error ************', end='\n')
        print(f'error: {str(error)}')
        print(usage_sample)
        sys.exit(2)

    inputdir = None
    outputdir = None
    for opt, arg in opts:
        if opt == '-h':
            print('************ help ************', end='\n')
            print(usage_sample)
            sys.exit()
        elif opt == "-i":
            inputdir = arg
            print(Fore.LIGHTCYAN_EX + f"-i {arg}" + Fore.RESET)
        elif opt == "-o":
            outputdir = arg
            print(Fore.LIGHTCYAN_EX + f"-o {arg}" + Fore.RESET)

    if inputdir and outputdir:
        process_svg_files(inputdir, outputdir)

