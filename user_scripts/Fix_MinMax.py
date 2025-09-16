#!/usr/bin/env python

import omero
from omero.gateway import BlitzGateway
import omero.scripts as scripts
from omero.rtypes import rlong, rstring, robject
import omero.util.script_utils as script_utils


def processImages(client, conn, scriptParams):
    """
    Process the script params to make a list of channel_offsets, then iterate
    through the images creating a new image from each with the specified
    channel offsets
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

    pixelsService = conn.getPixelsService()
    renderingService = conn.getRenderingSettingsService()

    # Get the channel offsets
    for image in images:
        min, max = 0, 65535
        for ann in image.listAnnotations():
            if isinstance(ann, omero.gateway.MapAnnotationWrapper):
                kvs = ann.getValue()
                for k, v in kvs:
                    if k == "MinSampleValue":
                        min = v
                    elif k == "MaxSampleValue":
                        max = v

        pi = image.getPrimaryPixels()
        pixelsService.setChannelGlobalMinMax(pi.getId(), 0, int(min), int(max), conn.SERVICE_OPTS)
        renderingService.setOriginalSettingsInImage(image.getId())

    return message


def runAsScript():

    dataTypes = [rstring('Image'), rstring('Dataset')]

    client = scripts.client(
        'Fix_MinMax.py',
        """Fix MinMax setting""",

        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Pick Images by 'Image' ID or by the ID of their "
            "Dataset'", values=dataTypes, default="Image"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Dataset IDs or Image IDs to "
            "process.").ofType(rlong(0)),

        version="1.0.0",
        authors=["Paul van Schayck"],
        institutions=["Maastricht University"],
        contact="p.vanschayck@maastrichtuniversity.nl",
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
