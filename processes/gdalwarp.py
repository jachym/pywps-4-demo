"""
Testing process for raster data manipulation
"""
__author__ = 'jachym'
__version__ = '1.0.0'

from pywps import Process, ComplexInput, ComplexOutput, get_format


class Warp(Process):
    """Implementation of gdalwarp as PyWPS Process
    """
    def __init__(self):
        inputs = [ComplexInput('raster',
                               'Raster input',
                               supported_formats=[get_format('GEOTIFF')])]

        outputs = [ComplexOutput('raster', 'Raster output', supported_formats=[get_format('GEOTIFF')])]

        super(Warp, self).__init__(
            self._handler,
            identifier='warp',
            title='GDAL Warp',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        """Perform something similar to gdalwarp
        """
        from osgeo import gdal
        inds = gdal.Open(request.inputs['raster'][0].file)
        outdriver = gdal.GetDriverByName('GTiff')
        outds = outdriver.CreateCopy('output.tiff', inds)
        outds.FlushCache()
        response.outputs['raster'].file = 'output.tiff'
        return response
