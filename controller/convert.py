
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict
from marker.output import save_output

import os

#=============================================================================#

class ConvertController():

    def __init__(self):
        pass

#-----------------------------------------------------------------------------#

    def PDF_to_MD(self, database_name):

        in_folder  = f"storage/{database_name}/save_PDF/"
        out_folder = f"storage/{database_name}/output_MD/"  

        in_folder  = os.path.abspath(in_folder)
        out_folder = os.path.abspath(out_folder)

        files = [file for file in os.listdir(in_folder)]
        files = [file for file in files if os.path.isfile(os.path.join(in_folder, file)) and file.lower().endswith('.pdf')]

        config_parser = ConfigParser({"output_format": "markdown"})

        converter = PdfConverter(
            artifact_dict  = create_model_dict(),
            config         = config_parser.generate_config_dict(),
            processor_list = config_parser.get_processors(),
            renderer       = config_parser.get_renderer()
            )

        for file in files:
            
            print(os.path.splitext(file)[0])

            os.makedirs(os.path.join(out_folder, os.path.splitext(file)[0]), exist_ok=True)

            rendered = converter(os.path.join(in_folder, file))

            save_output(rendered, os.path.join(out_folder, os.path.splitext(file)[0]), os.path.splitext(file)[0])

