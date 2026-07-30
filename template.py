import os 
import sys
from pathlib import Path
project_name ="ServicenowGamification"

import logging

#logging.basicConfig(level=logging.INFO,format='[%(asctime)s]:%(message)s:')

 
list_of_files=[
    ".github/workflows/.gitkeep", # .github -using this gitbub whenever using the CICD deployment so here actually we just write CICD related YAML automatic file so it will help you to do the cicd.lets say you want to commit your code in your GitHub .so whenever you will do the commit it automatically take your code from your github and it will do the deployemnt in your cloud so thats why this dot github important.
    f"src/{project_name}/__init__.py",
    f"src/{project_name}/Components/__init__.py",
    f"src/{project_name}/Config/__init__.py",
    f"src/{project_name}/Constant/__init__.py",
    f"src/{project_name}/Entity/__init__.py",
    f"src/{project_name}/Utils/__init__.py",
    f"src/{project_name}/PipeLine/__init__.py",
    "Config/Config.yaml",
    "dvc.yaml",
    "params.yaml",
    "requirments.txt",
    "setup.py",
    "Research/trails.ipynb",
    "Templates/index.html",
    "app.py",
    "main.py"

]

for filepath in list_of_files:
    filepath=Path(filepath)
    print(f" File path {filepath}")
    filedir,filename =os.path.split(filepath)

    if filedir !="":
        os.makedirs(filedir,exist_ok=True)
    if (not  os.path.exists(filepath) or os.path.getsize==0):
        with open(filepath,'w') as f:
            pass
            #logging.info(f"Creating the Empty File : {filepath}")
            print(f"Creating the Empty File : {filepath}")
    else:
        #logging.info(f"{filename} is already exists")
        print(f"{filename} is already exists")



