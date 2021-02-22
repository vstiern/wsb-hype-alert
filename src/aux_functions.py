"""Aux functions"""

from configparser import ConfigParser

# read file
def get_config_section(file_name="config.ini"):
    """
    Parse config file for target section.

    :param section_name: Section header name as string.
    :param file_name: File name of config file. Defualt name provided.
    :return: Dictionary with config name as keys and config value as value.
    """
    # create parser
    parser = ConfigParser()
    parser.read(file_name)
    return parser 






