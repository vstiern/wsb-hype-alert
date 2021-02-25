"""Aux functions"""

from pathlib import Path

from configparser import ConfigParser


# read file
def get_config_section(section, file_name="config.ini"):
    """
    Parse config file.

    :param section_name: Section header name as string.
    :param file_name: File name of config file. Defualt name provided.
    :return: Dictionary with config name as keys and config value as value.
    """
    # create parser
    parser = ConfigParser()
    file_path = Path(__file__).parent.parent
    parser.read(file_path / file_name)
    config_dict = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config_dict[param[0]] = param[1]
    else:
        raise Exception(f'Section: {section} not found in the {file_name}')
    return config_dict
