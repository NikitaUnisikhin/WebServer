import os


def get_path_to_data(host_name, file_name):
    return os.getcwd() + "\\sites\\" + f"\\{host_name}\\{file_name}"
