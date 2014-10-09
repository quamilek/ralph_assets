from threading import current_thread

from django.conf import settings

from ralph.account.models import Region


_requests = {}


def get_actual_regions():
    thread_name = current_thread().name
    if thread_name not in _requests:
        return Region.objects.filter(
            name=settings.DEFAULT_REGION_NAME,
        )
    return _requests[thread_name]['regions']


class RequestMiddleware(object):
    def process_request(self, request):
        if not request.user.is_anonymous():
            data = {
                'user_id': request.user.id,
                'regions': request.user.profile.get_regions(),
            }
            _requests[current_thread().name] = data

    def process_response(self, request, response):
        if not request.user.is_anonymous():
            _requests.pop(current_thread().name, None)
        return response
