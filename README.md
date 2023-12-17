1. [Architecture diagram]([url](https://github.com/pratik3221/docsumo/blob/master/ReportCardOcr.png)https://github.com/pratik3221/docsumo/blob/master/ReportCardOcr.png):
The authentication service is optional based on the introduction of a login/paid user feature to the service.

2. [Requirements.txt]([url](https://github.com/pratik3221/docsumo/blob/master/requirements.txt)https://github.com/pratik3221/docsumo/blob/master/requirements.txt) file:
Packages used to write code and test the service

3. [upload_image.py]([url](https://github.com/pratik3221/docsumo/blob/master/upload_image.py)https://github.com/pratik3221/docsumo/blob/master/upload_image.py):
- Basic REST API(POST) to accept the images in the allowed formats
- Do necessary operations on the image to improve data extraction using opencv
- Data extraction using pytessaract
- Formulate and return JSON response.
