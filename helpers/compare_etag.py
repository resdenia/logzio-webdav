def compare_file_etag(data, current):

    sorted_data = {}
    for etag in data:
        if etag == None:
            continue
        unique_code = etag[0:3] + "_" + etag.split("-")[1]
        if not unique_code in sorted_data:
            sorted_data[unique_code] = []
            sorted_data[unique_code].append(etag)
        else:
            sorted_data[unique_code].append(etag)
    return sorted_data
