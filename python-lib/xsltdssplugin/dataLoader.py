# -*- coding: utf-8 -*-
"""Module to get the root path, filename, and list of files of folders with the Dataiku API"""

import dataiku
from dataiku.customrecipe import *

class DataLoaderException(ValueError):
    """Custom exception raised if folder input/output is invalid"""
    pass
        
class dataLoader:
    def __init__(self, 
                 type_spec, 
                 role, 
                 input_arg=None, 
                 dss_folder=None, 
                 folder_path=None, 
                 files=None, 
                 files_path=None):
        
        if type_spec == "in":
            self.input_arg = get_input_names_for_role(role)
        elif type_spec == "out":
            self.input_arg = get_output_names_for_role(role)
        self.dss_folder = dataiku.Folder(self.input_arg[0])
        if type_spec == "out":
            self.folder_path = self.dss_folder.get_path() + "/"
        else:
            self.folder_path = self.dss_folder.get_path()
        self.files = files
        self.files_path = files_path
    
    @classmethod
    def fromUniqueFile(cls, type_spec, role):
        """Specific constructor to extract unique file from folder"""
        if type_spec == "in":
            input_arg = get_input_names_for_role(role)
        elif type_spec == "out":
            input_arg = get_output_names_for_role(role)
        dss_folder = dataiku.Folder(input_arg[0])
        folder_path = dss_folder.get_path()
        if len(dss_folder.list_paths_in_partition()) > 1:
            raise DataLoaderException(
            f"It seems folder contains more than one file for {role} role"
            )
        if len(dss_folder.list_paths_in_partition()) == 0:
            raise DataLoaderException(
            f"It seems folder is empty for {role} role"
            )
        else:
            files = dss_folder.list_paths_in_partition()[0]
        files_path = folder_path+files
        return cls(type_spec, role, input_arg, dss_folder, folder_path, files, files_path)
    
    @classmethod
    def fromMultipleFiles(cls, type_spec, role):
        """Specific constructor to extract multiples files from folder"""
        if type_spec == "in":
            input_arg = get_input_names_for_role(role)
        elif type_spec == "out":
            input_arg = get_output_names_for_role(role)
        dss_folder = dataiku.Folder(input_arg[0])
        folder_path = dss_folder.get_path()
        if len(dss_folder.list_paths_in_partition()) == 0:
            raise DataLoaderException(
            f"It seems folder is empty for {role} role"
            )
        else:
            files = dss_folder.list_paths_in_partition()
        files_path = [folder_path+file for file in files]
        return cls(type_spec, role, input_arg, dss_folder, folder_path, files, files_path)
