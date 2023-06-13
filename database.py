import os


def get_path_to_data(host_name, file_name):
    return os.getcwd() + f"{os.sep}sites{os.sep}" + f"{os.sep}{host_name}{os.sep}{file_name}"
