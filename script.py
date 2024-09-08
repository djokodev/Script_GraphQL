import subprocess
import os
import re


CMD_GENERATOR = {
    'mutations': "gqlg --schemaFilePath ./schema.graphql --destDirPath ./QUERIES_MUTATIONS --depthLimit 3",
    'queries': "gqlg --schemaFilePath ./schema.graphql --destDirPath ./QUERIES_MUTATIONS --depthLimit 5"
}

BASE_DIR = 'QUERIES_MUTATIONS'
MUTATIONS_DIR = os.path.join(BASE_DIR, 'mutations')
QUERIES_DIR = os.path.join(BASE_DIR, 'queries')
MUTATIONS_OUTPUT_FILE = 'mutations.py'
QUERIES_OUTPUT_FILE = 'queries.py'

def transform_query_name(name):
    name = re.sub(r'^\s*', '', name)
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
    return f"GET_{name.upper()}"

def gql_files_to_python_file(input_dir, output_file, command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Erreur lors de l'exécution de la commande : {result.stderr}")
        return

    with open(output_file, 'w') as outfile:
        for filename in os.listdir(input_dir):
            if filename.endswith('.gql'):
                file_path = os.path.join(input_dir, filename)
                with open(file_path, 'r') as infile:
                    content = infile.read()
                    name = os.path.splitext(filename)[0]
                    name = transform_query_name(name)
                    python_format = f"{name} = '''\n{content}\n'''\n\n"
                    outfile.write(python_format)


gql_files_to_python_file(MUTATIONS_DIR, MUTATIONS_OUTPUT_FILE, CMD_GENERATOR['mutations'])
gql_files_to_python_file(QUERIES_DIR, QUERIES_OUTPUT_FILE, CMD_GENERATOR['queries'])
