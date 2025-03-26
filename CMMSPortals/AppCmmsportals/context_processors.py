from django.conf import settings
import os

def resource_processor(request):
    """
    Context processor to handle static resource URLs similar to Flask's get_resource_url
    """
    def get_resource_url(url):
        """Convert CDN URLs to local static paths if needed"""
        # Map of CDN URLs to local paths
        cdn_map = {
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css': 
                'css/bootstrap.min.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css': 
                'css/all.min.css',
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js': 
                'js/bootstrap.bundle.min.js'
        }
        
        if url in cdn_map:
            return os.path.join(settings.STATIC_URL, cdn_map[url])
        return url
    
    return {'get_resource_url': get_resource_url}
