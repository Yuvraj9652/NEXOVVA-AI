import logging
import threading
from apps.broadcast.models import Campaign

logger = logging.getLogger("analytics_service")


class AnalyticsDispatcher:
    @classmethod
    def dispatch_event(cls, organization, campaign, event_type: str, details: dict) -> None:
        """
        Emits an analytics event. Fires a background worker thread so the main conversation
        engine does not block while performing database aggregations.
        """
        logger.info(f"Analytics event received: {event_type} - Campaign: {campaign.id if campaign else 'None'}")
        
        # Run event processing synchronously in tests to avoid SQLite concurrency locks,
        # otherwise run in a separate background thread.
        import sys
        if "test" in sys.argv or "test_coverage" in sys.argv:
            cls._process_event(organization, campaign, event_type, details)
            return

        thread = threading.Thread(
            target=cls._process_event,
            args=(organization, campaign, event_type, details)
        )
        thread.daemon = True
        thread.start()

    @classmethod
    def _process_event(cls, organization, campaign, event_type: str, details: dict) -> None:
        """Processes the analytics event in the background."""
        try:
            if not campaign:
                return

            if event_type == "reply":
                # Increment campaign replies and interested counters
                campaign.replied += 1
                buying_intent = details.get("buying_intent", "LOW")
                if buying_intent in ["HIGH", "MEDIUM"]:
                    campaign.interested += 1
                
                campaign.save(update_fields=["replied", "interested"])
                logger.info(f"Updated analytics for Campaign: {campaign.id} - Replied: {campaign.replied}, Interested: {campaign.interested}")
        except Exception as e:
            logger.error(f"Failed to process background analytics event: {e}", exc_info=True)
