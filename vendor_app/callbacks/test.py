import concurrent.futures

from flask import request


def validate_file(file):
    # lambda function.... to validate extension
    pass


def upload():
    files = request.files.getlist('files')
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(validate_file, file): file for file in files}
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
            except Exception as e:
                result = {file.filename: str(e)}
            results.append(result)
    return results
