import cloudinary.uploader
from rest_framework.response import Response
from rest_framework import status



class CloudinaryUploader:
    IMAGE_FOLDER = 'CRM'

    # Upload an image to Cloudinary and return a Response in all cases.
    @staticmethod
    def upload_attachment(image, folder: str = None):
        if not image:
            return {"success": False, "message": "Image is not provided"}
        
        target_folder = folder or CloudinaryUploader.IMAGE_FOLDER
        try:
            result = cloudinary.uploader.upload(
                image,
                folder=target_folder,
                resource_type='image'
            )
            url = result.get('secure_url')
            public_id = result.get('public_id')
            return {"success": True, "url": url, "public_id": public_id}
        except Exception as e:
            return {"success": False, "message": str(e)}


    @staticmethod
    def delete_files(public_id):
        if not public_id:
            return {"success": False, "message": "public_id not found"}
        try:
            result = cloudinary.uploader.destroy(public_id)
            return {"success": True, "message": "Image deleted successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}