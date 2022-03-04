from rest_framework import renderers
from rest_framework.settings import reload_api_settings

import json
class UserRender(renderers.JSONRenderer):
  charset = 'utf-8'

  def render(self, data, accepted_media_type, renderer_context):

      response = ''

      if 'ErrorDetail' in str(data):
        response = json.dumps({'errors': data})

      else:
        response = json.dumps({'data': data})


      return response
      #return super().render(data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)