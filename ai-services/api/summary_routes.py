from fastapi import APIRouter

from api.schemas import (
    MeetingSummaryRequest,
    MeetingSummaryResponse,
)

from services.summary_service import generate_meeting_summary

router = APIRouter(
    prefix="/meeting-summary",
    tags=["Meeting AI"],
)


@router.post("/", response_model=MeetingSummaryResponse)
async def meeting_summary(
    request: MeetingSummaryRequest,
):
    result = await generate_meeting_summary(
        request.transcript
    )

    return MeetingSummaryResponse(**result)