#!/usr/bin/env python

import omero
from omero.gateway import BlitzGateway
import omero.scripts as scripts
from omero.rtypes import rlong, rstring, robject, rfloat
import omero.util.script_utils as script_utils


def processImages(client, conn, scriptParams):
    """
    Process the script params t, then iterate
    through the images
    """

    message = ""

    # Get the images
    objects, logMessage = script_utils.getObjects(conn, scriptParams)
    message += logMessage
    if not objects:
        return None, None, message

    # Concatenate images from datasets
    if scriptParams["Data_Type"] == "Image":
        images = objects
    else:
        images = []
        for ds in objects:
            images += ds.listChildren()

    updateService = conn.getUpdateService()

    # Use custom pixel size if provided, otherwise use default
    pixelSize = scriptParams.get("Pixel_Size", 3.81)
    pixSize = omero.model.LengthI(pixelSize, omero.model.enums.UnitsLength.NANOMETER)

    # Get the channel offsets
    for image in images:
         metadata = dict(image.loadOriginalMetadata()[1])
         pi = image.getPrimaryPixels()
         pixels = pi._obj

         pixels.setPhysicalSizeX(pixSize)
         pixels.setPhysicalSizeY(pixSize)

         updateService.saveObject(pixels)

    return message


def runAsScript():

    dataTypes = [rstring('Image'), rstring('Dataset')]

    client = scripts.client(
        'Fix_PixelSize.py',
        """Fix PixelSize settings. Enter The Image or Dataset ID.
           Specify a custom pixel size in nanometers. If left empty, 3.81 nm will be used.
        """,

        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Pick Images by 'Image' ID or by the ID of their "
            "Dataset'", values=dataTypes, default="Image"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Dataset IDs or Image IDs to "
            "process.").ofType(rlong(0)),

        scripts.Float(
            "Pixel_Size", optional=True, grouping="3",
            description="Custom pixel size in nanometers",
            default=float(3.81)),

        version="1.0.2",
        authors=["Paul van Schayck", "Chris Lewis"],
        institutions=["Maastricht University"],
        contact="chris.lewis@maastrichtuniversity.nl",
    )

    try:
        scriptParams = client.getInputs(unwrap=True)

        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)

        message = processImages(client, conn, scriptParams)

        # Return message, new image and new dataset (if applicable) to the
        # client
        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()

if __name__ == "__main__":
    runAsScript()