import os
import tempfile

__author__ = 'Brauni'

from pywps import Process, LiteralInput, ComplexInput, ComplexOutput, Format, get_format


class Buffer(Process):
    def __init__(self):
        inputs = [ComplexInput('poly_in', 'Input1',
                               supported_formats=[get_format('GML')],
                               max_occurs='2'),
                  LiteralInput('buffer', 'Buffer', data_type='float')
                 ]
        outputs = [ComplexOutput('buff_out', 'Buffered', supported_formats=[get_format('GML')])]

        super(Buffer, self).__init__(
            self._handler,
            identifier='buffer',
            version='0.1',
            title="Brauni's 1st process",
            abstract='This process is the best ever being coded',
            profile='',
            metadata=['Process', '1st', 'Hilarious'],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        from osgeo import ogr

        inSource = ogr.Open(request.inputs['poly_in'][0].file)

        inLayer = inSource.GetLayer()
        out = inLayer.GetName()
        outPath = os.path.join(tempfile.gettempdir(), out)

        # create output file
        driver = ogr.GetDriverByName('GML')
        outSource = driver.CreateDataSource(outPath, ["XSISCHEMAURI=http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        outLayer = outSource.CreateLayer(out, None, ogr.wkbUnknown)

        # for each feature
        featureCount = inLayer.GetFeatureCount()
        index = 0
        import time

        while index < featureCount:
            # get the geometry
            inFeature = inLayer.GetNextFeature()
            inGeometry = inFeature.GetGeometryRef()

            # make the buffer
            buff = inGeometry.Buffer(float(request.inputs['buffer'][0].data))

            # create output feature to the file
            outFeature = ogr.Feature(feature_def=outLayer.GetLayerDefn())
            outFeature.SetGeometryDirectly(buff)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()  # makes it crash when using debug
            index += 1

            time.sleep(1)  # making things little bit slower
            response.update_status("Calculating buffer for feature %d from %d" % (index + 1, featureCount),
                                   (100 * (index + 1) / featureCount * 1))

        response.outputs['buff_out'].data_format = get_format('GML')
        response.outputs['buff_out'].file = outPath

        return response

