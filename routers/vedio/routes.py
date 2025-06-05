from fastapi import APIRouter
from fastapi.responses import JSONResponse

from routers.banner.request_types import CreateVedioScriptRequest
from services.vedio_service import VedioService


router = APIRouter(prefix="/vedio", tags=["Vedio"])


@router.post("/generate_vedio_ad")
async def create_vedio_script(
    # vedio_script_req: CreateVedioScriptRequest
):
    """Create a vedio script for the product"""

    try:
        vedio_service = VedioService()
        # prompt = await vedio_service.generate_add_script(vedio_script_req.product_info)
        prompt = await vedio_service.generate_add_script({})
        vedio = await vedio_service.create_vedio(prompt)

        return JSONResponse(content={"success": True, "vedio": vedio}, status_code=200)

    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "error": str(e),
                "message": "Failed to generate video script",
            },
            status_code=500,
        )
