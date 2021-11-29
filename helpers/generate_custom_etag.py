def generate_etag(etag):
    return etag[0:3] + "_" + etag.split("-")[1]
