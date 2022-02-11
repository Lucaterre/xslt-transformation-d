# -*- coding: utf-8 -*-

from dataiku.customrecipe import *

from xsltdssplugin.dataLoader import dataLoader
from xsltdssplugin.XMLUtils import XML, XSLTTransformation, Schema, SchemaValidation

#
# Global scenario
#

# Load user parameters 
user_params = get_recipe_config()

# Read input / output folder
xml_files = dataLoader.fromMultipleFiles(type_spec="in", role="xml_origin_folder")
xslt_stylesheet = dataLoader.fromUniqueFile(type_spec="in", role="xslt_origin_folder")
xml_out_folder = dataLoader(type_spec="out", role="xslt_output_folder")
if user_params['use_validation']:
    # exception if user say yes to validation but there are not schema or folder
    schema = dataLoader.fromUniqueFile(type_spec="in", role="validation_folder")

# A. XSLT transformation    
print("=========| XSLT Transformation start |=========")
xslt = XML(xslt_stylesheet.files_path, role="XSLT").source_parse
for xml_filename in xml_files.files_path:
    transform_view = XSLTTransformation(xml_filename, xslt, xml_out_folder.folder_path, user_params)
    transform_view._apply_XSLT_transformation()
print("=========| XSLT Transformation end |=========")

# B. XML Validation
if user_params['use_validation']:
    schema = Schema(schema.files_path)    
    for new_xml in xml_out_folder.dss_folder.list_paths_in_partition():
        validation_view = SchemaValidation(xml_out_folder.folder_path+new_xml, schema.schema_in)._validator()

print("=========| Process Finished |=========")
