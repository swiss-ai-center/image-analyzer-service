from common_code.config import get_settings
from common_code.logger.logger import get_logger, Logger
from common_code.service.models import Service
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common_code.tasks.models import TaskData
# Imports required by the service's model
import io
import json
from PIL import Image
from PIL.ExifTags import TAGS

api_description = """
This service analyzes images. It returns the following information:
- Format (e.g. image/jpeg)
- Image width (e.g. 1920)
- Image length (e.g. 1080)
- Bits per sample (e.g. (8, 8, 8))
- Photometric interpretation (e.g. 2)
- Resolution unit (e.g. 3)
- Exif offset (e.g. 236)
- Software (e.g. Adobe Photoshop CC 2017 (Macintosh))
- Orientation (e.g. 1)
- Date time (e.g. 2017:05:02 16:00:48)
- Samples per pixel (e.g. 3)
- X resolution (e.g. 118.1102)
- Y resolution (e.g. 118.1102)
"""
api_summary = """
Analyze images. Returns metadata information about the image.
"""
api_title = "Image Analyzer API."
version = "1.0.0"

settings = get_settings()


class MyService(Service):
    """
    Image analyzer model
    """

    # Any additional fields must be excluded for Pydantic to work
    _model: object
    _logger: Logger

    def __init__(self):
        super().__init__(
            name="Image Analyzer",
            slug="image-analyzer",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.APPLICATION_JSON]),
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.IMAGE_PROCESSING,
                    acronym=ExecutionUnitTagAcronym.IMAGE_PROCESSING
                ),
            ],
            has_ai=False,
            docs_url="https://docs.swiss-ai-center.ch/reference/services/image-analyzer/",
        )
        self._logger = get_logger(settings)

    def process(self, data):
        raw = data["image"].data
        stream = io.BytesIO(raw)
        img = Image.open(stream)
        metadata = {"Format": img.get_format_mimetype()}

        exif = img.getexif()
        for tagId, val in exif.items():
            name = TAGS[tagId] if tagId in TAGS else "0x{tagId:x}".format(tagId=tagId)
            metadata[name] = val if type(val) in [str, int, float, bool] else str(val)

        return {
            "result": TaskData(
                data=json.dumps(metadata),
                type=FieldDescriptionType.APPLICATION_JSON
            )
        }
