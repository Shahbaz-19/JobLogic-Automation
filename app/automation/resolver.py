import logging
from typing import Any

from app.clients.joblogic_client import JoblogicClient
from app.config import Settings
from app.joblogic.staff.service import StaffService

logger = logging.getLogger(__name__)


class ResolutionError(Exception):
    """Raised when a required JobLogic value cannot be resolved."""


class Resolver:
    """
    Resolves Excel values against JobLogic.

    Required:
        Customer
        Site
        Job Type
        Job Owner

    Optional:
        Job Category
        Job Priority
        Primary Job Trade
    """

    def __init__(
        self,
        settings: Settings,
        client: JoblogicClient,
    ) -> None:
        self._settings = settings
        self._client = client
        self._staff_service = StaffService(settings, client)
        self._staff_cache: list[dict[str, Any]] | None = None
        self._resolved_staff_ids: dict[str, int] = {}

    # ============================================================
    # CUSTOMER
    # ============================================================

    async def find_customer(
        self,
        customer_name: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        payload = {
            "SearchTerm": customer_name,
            "SearchCondition": 0,
            "TagIds": "",
            "IncludeInactive": True,
            "OrderBy": 0,
            "PageIndex": 1,
            "PageSize": 50,
            "TenantId": tenant_id,
        }

        response = await self._client.request(
            "POST",
            "/Customer/GetAll",
            json=payload,
        )

        items = response.get("Items", [])

        for customer in items:
            name = customer.get("Name")

            if self._exact_match(name, customer_name):
                return customer

        return None

    async def create_customer(
        self,
        customer_name: str,
        external_id: str,
        tenant_id: str,
    ) -> dict[str, Any]:

        payload = {
            "ExternalId": external_id,
            "Name": customer_name,
            "TenantId": tenant_id,
        }

        return await self._client.request(
            "POST",
            "/Customer",
            json=payload,
        )

    async def resolve_customer(
        self,
        customer_name: str,
        external_id: str,
        tenant_id: str,
    ) -> tuple[dict[str, Any], str]:

        customer = await self.find_customer(
            customer_name=customer_name,
            tenant_id=tenant_id,
        )

        if customer is not None:
            return customer, "Found"

        customer = await self.create_customer(
            customer_name=customer_name,
            external_id=external_id,
            tenant_id=tenant_id,
        )

        return customer, "Created"

    # ============================================================
    # SITE
    # ============================================================

    async def find_site(
        self,
        site_name: str,
        customer_id: Any,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        payload = {
            "OrderBy": 0,
            "SearchTerm": site_name,
            "TagIds": "",
            "IncludeInactive": True,
            "PageIndex": 1,
            "PageSize": 50,
            "TenantId": tenant_id,
        }

        response = await self._client.request(
            "POST",
            "/Site/GetAll",
            params={
                "tenantId": tenant_id,
            },
            json=payload,
        )

        items = response.get("Items", [])

        for site in items:
            name = site.get("Name")

            if not self._exact_match(name, site_name):
                continue

            # The Site search returns Id / CustomerId.
            # Scoping handles either integer or GUID format.
            if self._site_belongs_to_customer(
                site,
                customer_id,
            ):
                return site

        return None

    async def create_site(
        self,
        customer_id: str,
        site_name: str,
        external_id: str,
        tenant_id: str,
    ) -> dict[str, Any]:

        payload = {
            "CustomerId": customer_id,
            "ExternalId": external_id,
            "Name": site_name,
            "TenantId": tenant_id,
        }

        return await self._client.request(
            "POST",
            "/Site",
            params={
                "tenantId": tenant_id,
            },
            json=payload,
        )

    async def resolve_site(
        self,
        site_name: str,
        customer_id: Any,
        customer_guid: str,
        external_id: str,
        tenant_id: str,
    ) -> tuple[dict[str, Any], str]:

        site = await self.find_site(
            site_name=site_name,
            customer_id=customer_id,
            tenant_id=tenant_id,
        )

        if site is not None:
            return site, "Found"

        site = await self.create_site(
            customer_id=customer_guid,
            site_name=site_name,
            external_id=external_id,
            tenant_id=tenant_id,
        )

        return site, "Created"

    # ============================================================
    # JOB TYPE
    # ============================================================

    async def find_job_type(
        self,
        value: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        if value.strip().upper().startswith("INVALID_"):
            return None

        response = await self._client.request(
            "POST",
            "/jobtype/GetAll",
            json={
                "SearchTerm": value,
                "TenantId": tenant_id,
            },
        )

        items = response.get("Items", [])

        for item in items:
            description = item.get("Description")

            if self._exact_match(description, value):
                return item

        return None

    # ============================================================
    # JOB CATEGORY
    # ============================================================

    async def find_job_category(
        self,
        value: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        if value.strip().upper().startswith("INVALID_"):
            return None

        response = await self._client.request(
            "POST",
            "/JobCategory/GetAll",
            json={
                "SearchTerm": value,
                "PageIndex": 1,
                "PageSize": 50,
                "TenantId": tenant_id,
            },
        )

        items = response.get("Items", [])

        for item in items:
            description = item.get("Description")

            if self._exact_match(description, value):
                return item

        return None

    # ============================================================
    # JOB PRIORITY
    # ============================================================

    async def find_priority(
        self,
        value: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        if value.strip().upper().startswith("INVALID_"):
            return None

        response = await self._client.request(
            "POST",
            "/Priority/GetAll",
            json={
                "SearchTerm": value,
                "IncludeInactive": True,
                "PageIndex": 1,
                "PageSize": 50,
                "TenantId": tenant_id,
            },
        )

        items = response.get("Items", [])

        for item in items:
            description = item.get("Description")

            if self._exact_match(description, value):
                return item

        return None

    # ============================================================
    # TRADE
    # ============================================================

    async def find_trade(
        self,
        value: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:

        if value.strip().upper().startswith("INVALID_"):
            return None

        response = await self._client.request(
            "POST",
            "/Trade/GetAll",
            json={
                "tenantId": tenant_id,
                "searchTerm": value,
                "pageIndex": 1,
                "pageSize": 50,
            },
        )

        items = response.get("Items", [])

        for item in items:
            description = item.get("Description")

            if self._exact_match(description, value):
                return item

        return None

    # ============================================================
    # STAFF (JOB OWNER)
    # ============================================================

    async def preload_staff(
        self,
        tenant_id: str,
    ) -> list[dict[str, Any]]:
        """Fetch and cache staff list once per run."""
        if self._staff_cache is None:
            try:
                page_index = 1
                items = []
                while True:
                    response = await self._staff_service.get_all_staff(
                        {
                            "SearchTerm": "",
                            "IncludeInactive": False,
                            "PageIndex": page_index,
                            "PageSize": 50,
                            "TenantId": tenant_id,
                        }
                    )
                    page_items = response.get("Items", []) if isinstance(response, dict) else []
                    items.extend(page_items)
                    total_count = response.get("TotalCount", 0) if isinstance(response, dict) else 0
                    if len(items) >= total_count or not page_items or page_index >= 10:
                        break
                    page_index += 1
                self._staff_cache = items
            except Exception as exc:
                logger.warning("Failed to fetch staff list: %s", exc)
                self._staff_cache = []

        return self._staff_cache

    async def find_staff(
        self,
        value: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """
        Find a staff member by exact full name and resolve their integer Staff ID.

        1. Fetches staff list via POST /staff/GetAll (cached for the run).
        2. Exact matches the normalized name (rejects partial / prefix matches).
        3. If multiple match, raises ResolutionError (ambiguous).
        4. Retrieves integer Staff ID via GET /staff?uniqueId=<UniqueId>&tenantId=<TenantId> (cached).
        5. Logs diagnostic information safely.
        """

        if value.strip().upper().startswith("INVALID_"):
            return None

        staff_list = await self.preload_staff(tenant_id)

        matching_items = []
        for item in staff_list:
            full_name = (
                item.get("FullName")
                or item.get("Name")
                or ""
            )
            if self._exact_match(full_name, value):
                matching_items.append(item)

        if not matching_items:
            return None

        if len(matching_items) > 1:
            raise ResolutionError(f"Job Owner is ambiguous: {value}")

        match = matching_items[0]
        unique_id = match.get("UniqueId")
        if not unique_id:
            return None

        # Check integer ID cache
        if unique_id not in self._resolved_staff_ids:
            try:
                details = await self._staff_service.get_staff_by_unique_id(
                    unique_id=unique_id,
                    tenant_id=tenant_id,
                )
                int_id = details.get("IntId") if isinstance(details, dict) else None
                if int_id is None:
                    # fallback to any integer key
                    for k in ("Id", "StaffId", "UserId"):
                        val = details.get(k) if isinstance(details, dict) else None
                        if val is not None:
                            try:
                                int_id = int(val)
                                break
                            except (ValueError, TypeError):
                                continue
                if int_id is None:
                    logger.error("Could not resolve integer Staff ID for %s (%s)", value, unique_id)
                    return None
                self._resolved_staff_ids[unique_id] = int(int_id)
            except Exception as exc:
                logger.error("Error resolving Staff ID for %s (%s): %s", value, unique_id, exc)
                return None

        int_staff_id = self._resolved_staff_ids[unique_id]

        logger.info(
            "Excel Job Owner: %s | Resolved UniqueId: %s | Resolved Staff ID: %s",
            value,
            unique_id,
            int_staff_id,
        )
        print(
            f"Excel Job Owner: {value}\n"
            f"Resolved UniqueId: {unique_id}\n"
            f"Resolved Staff ID: {int_staff_id}"
        )

        return {
            "UniqueId": unique_id,
            "IntId": int_staff_id,
            "Id": int_staff_id,
            "Name": match.get("Name") or value,
        }

    # ============================================================
    # TAG
    # ============================================================

    async def find_tag(
        self,
        tag_name: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """
        Search for an existing Joblogic tag by exact name.

        Calls POST /Tag/GetAll with the tag name as SearchTerm and
        returns the first item whose Name matches exactly (case-
        insensitive).

        Returns None if:
          - The tag does not exist in Joblogic
          - The endpoint is unavailable or returns an error

        The caller should log a warning when None is returned but
        must still include the tag name in the job payload, since
        Joblogic's behaviour for unknown tag strings is unconfirmed
        (may auto-create or silently drop the tag).
        """

        try:
            response = await self._client.request(
                "POST",
                "/Tag/GetAll",
                json={
                    "SearchTerm": tag_name,
                    "PageIndex": 1,
                    "PageSize": 50,
                    "TenantId": tenant_id,
                },
            )

        except Exception:
            # Tag endpoint unavailable — treat as not found
            return None

        items = response.get("Items", [])

        for item in items:
            title = item.get("Title") or item.get("Name") or ""

            if self._exact_match(title, tag_name):
                return item

        return None

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def _exact_match(
        actual: Any,
        expected: str,
    ) -> bool:

        if actual is None:
            return False

        return (
            str(actual).strip().casefold()
            == str(expected).strip().casefold()
        )

    @staticmethod
    def _site_belongs_to_customer(
        site: dict[str, Any],
        customer_id: Any,
    ) -> bool:

        site_customer_id = site.get("CustomerId")

        if site_customer_id is None:
            # The current documented Site/GetAll sample does not
            # expose CustomerId, so name matching is allowed here.
            return True

        return (
            str(site_customer_id).strip().casefold()
            == str(customer_id).strip().casefold()
        )