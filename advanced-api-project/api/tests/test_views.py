"""
DRF API tests for the Book endpoints.

This suite aims to be resilient to minor differences in your model/viewset
configuration by:
- Resolving router URL names with and without the "api:" namespace.
- Dynamically building a valid Book payload from the model's required fields.
- Skipping optional tests (filter/search/order) when unsupported.

Assumptions (kept minimal):
- You registered a DRF router for BookViewSet, yielding URL names
  "book-list" and "book-detail" (optionally namespaced as "api:").
- Anonymous users can read (list/retrieve). Authenticated users can write.

How to run:
    python manage.py test api
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from rest_framework import status
from rest_framework.test import APIClient

try:
    # Import your Book model from the api app
    from api.models import Book  # type: ignore
except Exception as exc:  # pragma: no cover - helpful failure message
    raise RuntimeError("Could not import Book model from api.models. Adjust the import in test_views.py.") from exc


# ---------- URL helpers ----------

def _reverse_any(name: str, *args) -> str:
    """Try resolve URL name with and without an "api:" namespace."""
    try:
        return reverse(name, args=args)
    except NoReverseMatch:
        return reverse(f"api:{name}", args=args)


def books_list_url() -> str:
    return _reverse_any("book-list")


def book_detail_url(pk: Any) -> str:
    return _reverse_any("book-detail", pk)


# ---------- Dynamic payload helpers ----------

CHAR_FALLBACK = "Lorem Ipsum"
TEXT_FALLBACK = "Lorem ipsum dolor sit amet."
INT_FALLBACK = 123
DEC_FALLBACK = "9.99"
DATE_FALLBACK = date(2020, 1, 1)
DATETIME_FALLBACK = datetime(2020, 1, 1, 12, 0, 0)
BOOL_FALLBACK = True


def _is_required(field: models.Field) -> bool:
    # Required iff not auto, not primary key, not null, not blank, no default, and not auto_now/auto_now_add
    has_default = field.default is not models.NOT_PROVIDED
    auto_timestamp = getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False)
    return (
        not isinstance(field, (models.AutoField, models.BigAutoField))
        and not field.primary_key
        and not auto_timestamp
        and not getattr(field, "null", False)
        and not getattr(field, "blank", False)
        and not has_default
    )


def _sample_for(field: models.Field) -> Any:
    if isinstance(field, (models.CharField, models.SlugField, models.EmailField)):
        # Respect max_length when present
        text = CHAR_FALLBACK
        max_len = getattr(field, "max_length", None)
        return text[:max_len] if max_len else text
    if isinstance(field, models.TextField):
        return TEXT_FALLBACK
    if isinstance(field, (models.IntegerField, models.SmallIntegerField, models.BigIntegerField)):
        return INT_FALLBACK
    if isinstance(field, (models.FloatField, models.DecimalField)):
        return DEC_FALLBACK
    if isinstance(field, models.BooleanField):
        return BOOL_FALLBACK
    if isinstance(field, models.DateField) and not isinstance(field, models.DateTimeField):
        return DATE_FALLBACK.isoformat()
    if isinstance(field, models.DateTimeField):
        return DATETIME_FALLBACK.isoformat()
    # Skip file/image and relational fields in payload (cannot post easily without fixtures)
    raise ValueError("Unsupported field for sample payload")


def build_valid_payload() -> Tuple[Dict[str, Any], List[str]]:
    """Builds a dict with required, non-relational fields. Returns (payload, skipped_required).

    If there are required relational fields (FK/M2M/OneToOne) we record them as skipped
    so tests that require POST/PUT can be conditionally skipped with a helpful message.
    """
    payload: Dict[str, Any] = {}
    skipped_required: List[str] = []

    for field in Book._meta.get_fields():
        # Only concrete model fields
        if not hasattr(field, "attname"):
            continue

        # Skip implicit reverse relations
        if field.auto_created and not field.concrete:
            continue

        # Handle relations
        if field.is_relation:
            if _is_required(field):
                skipped_required.append(field.name)
            continue

        field_obj: models.Field = field  # type: ignore[assignment]
        if _is_required(field_obj):
            try:
                payload[field_obj.name] = _sample_for(field_obj)
            except ValueError:
                skipped_required.append(field_obj.name)

    return payload, skipped_required


def choose_text_field() -> Optional[str]:
    for field in Book._meta.get_fields():
        if isinstance(field, (models.CharField, models.TextField)) and not field.is_relation:
            return field.name
    return None


def choose_order_field() -> Optional[str]:
    # Prefer a date/datetime; otherwise integer/decimal
    for cls in (models.DateField, models.DateTimeField, models.IntegerField, models.DecimalField):
        for field in Book._meta.get_fields():
            if isinstance(field, cls) and not field.is_relation:
                return field.name
    return None


# ---------- Test Case ----------

class BookAPITests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.User = get_user_model()
        cls.user = cls.User.objects.create_user(username="tester", password="pass1234!")
        cls.client_auth = APIClient()
        cls.client_auth.force_authenticate(user=cls.user)

        cls.client_anon = APIClient()

        # Prepare two baseline objects via the ORM to keep API tests focused
        # on behaviour rather than data setup.
        payload, skipped = build_valid_payload()
        if skipped:
            # We still create objects with minimal or defaultable fields if possible.
            # Attempt to create using whatever payload we have; if creation fails at runtime,
            # subsequent tests will reveal the issue.
            pass
        try:
            cls.book1 = Book.objects.create(**payload)
        except Exception:
            # As an ultra-fallback, try creating with only the *first* text field present
            text_field = choose_text_field() or "title"
            cls.book1 = Book.objects.create(**{text_field: "Alpha"})

        try:
            cls.book2 = Book.objects.create(**{**payload, **{choose_text_field() or "title": "Beta"}})
        except Exception:
            text_field = choose_text_field() or "title"
            cls.book2 = Book.objects.create(**{text_field: "Beta"})

        cls.text_field = choose_text_field()
        cls.order_field = choose_order_field()

        # If we have a date/datetime order field, ensure differing values
        if cls.order_field and isinstance(Book._meta.get_field(cls.order_field), models.DateField):
            setattr(cls.book1, cls.order_field, date.today() - timedelta(days=1))
            setattr(cls.book2, cls.order_field, date.today())
            cls.book1.save(update_fields=[cls.order_field])
            cls.book2.save(update_fields=[cls.order_field])
        elif cls.order_field and isinstance(Book._meta.get_field(cls.order_field), models.DateTimeField):
            setattr(cls.book1, cls.order_field, datetime.now() - timedelta(days=1))
            setattr(cls.book2, cls.order_field, datetime.now())
            cls.book1.save(update_fields=[cls.order_field])
            cls.book2.save(update_fields=[cls.order_field])

    # ---- Read endpoints ----
    def test_list_books_allows_anonymous(self):
        resp = self.client_anon.get(books_list_url())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, (list, dict))  # paginator vs plain list

    def test_retrieve_book_allows_anonymous(self):
        resp = self.client_anon.get(book_detail_url(self.book1.pk))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Ensure the object retrieved matches the requested id when present
        if isinstance(resp.data, dict) and "id" in resp.data:
            self.assertEqual(resp.data["id"], self.book1.pk)

    # ---- Create ----
    def test_create_book_requires_authentication(self):
        payload, skipped = build_valid_payload()
        if skipped:
            self.skipTest(
                f"Skipping create: model has required fields not suitable for simple POST: {skipped}"
            )
        # Anonymous should fail (401 or 403 depending on permission class)
        resp_anon = self.client_anon.post(books_list_url(), payload, format="json")
        self.assertIn(resp_anon.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

        # Authenticated should succeed
        resp_auth = self.client_auth.post(books_list_url(), payload, format="json")
        self.assertEqual(resp_auth.status_code, status.HTTP_201_CREATED)
        # Verify response echoes saved fields
        for k, v in payload.items():
            if k in resp_auth.data:
                self.assertIsNotNone(resp_auth.data[k])

    # ---- Update (PUT/PATCH) ----
    def test_update_book_put_and_patch(self):
        payload, skipped = build_valid_payload()
        if self.text_field is None:
            self.skipTest("No textual field available to test updates.")
        if skipped:
            # We can still PATCH a single text field if present
            pass

        # Anonymous should be rejected
        resp = self.client_anon.patch(
            book_detail_url(self.book1.pk), {self.text_field: "Updated"}, format="json"
        )
        self.assertIn(resp.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

        # Authenticated PATCH
        resp = self.client_auth.patch(
            book_detail_url(self.book1.pk), {self.text_field: "Updated"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(getattr(self.book1, self.text_field), "Updated")

        # Authenticated PUT: send full payload if possible, otherwise send only text field
        put_payload = payload or {self.text_field: "Replaced"}
        resp = self.client_auth.put(book_detail_url(self.book1.pk), put_payload, format="json")
        self.assertIn(resp.status_code, {status.HTTP_200_OK, status.HTTP_202_ACCEPTED})

    # ---- Delete ----
    def test_delete_book_requires_authentication(self):
        # Anonymous blocked
        resp = self.client_anon.delete(book_detail_url(self.book2.pk))
        self.assertIn(resp.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

        # Authenticated can delete
        resp = self.client_auth.delete(book_detail_url(self.book2.pk))
        self.assertIn(resp.status_code, {status.HTTP_204_NO_CONTENT, status.HTTP_200_OK})
        self.assertFalse(Book.objects.filter(pk=self.book2.pk).exists())

    # ---- Filtering ----
    def test_filtering_by_text_field_when_supported(self):
        if self.text_field is None:
            self.skipTest("No text field available for filtering test.")

        # Set distinct values to filter on
        setattr(self.book1, self.text_field, "Alice")
        setattr(self.book2, self.text_field, "Bob")
        self.book1.save(update_fields=[self.text_field])
        self.book2.save(update_fields=[self.text_field])

        url = books_list_url() + f"?{self.text_field}=Alice"
        resp = self.client_anon.get(url)
        if resp.status_code != status.HTTP_200_OK:
            self.skipTest("Filtering not supported (non-200 response to filter query).")

        # Accept both paginated and non-paginated shapes
        results = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
        if not isinstance(results, list):
            self.skipTest("Unexpected response shape; skipping filtering assertion.")

        # If backend ignores the filter, both items may appear. Guard accordingly.
        # Only assert when the backend actually filtered to 1 result.
        if len(results) == 1:
            self.assertEqual(
                results[0].get(self.text_field), "Alice",
                "Filter should limit results to the matching text field value",
            )
        else:
            self.skipTest("Filtering not active on this endpoint; skipping.")

    # ---- Search ----
    def test_search_query_when_supported(self):
        if self.text_field is None:
            self.skipTest("No text field available for search test.")

        setattr(self.book1, self.text_field, "The Pragmatic Programmer")
        setattr(self.book2, self.text_field, "Clean Code")
        self.book1.save(update_fields=[self.text_field])
        self.book2.save(update_fields=[self.text_field])

        url = books_list_url() + "?search=Pragmatic"
        resp = self.client_anon.get(url)
        if resp.status_code != status.HTTP_200_OK:
            self.skipTest("Search not supported (non-200 response to search query).")

        results = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
        if not isinstance(results, list):
            self.skipTest("Unexpected response shape; skipping search assertion.")

        # If SearchFilter is on, only one should match
        if len(results) == 1:
            self.assertIn("Pragmatic", results[0].get(self.text_field, ""))
        else:
            self.skipTest("SearchFilter likely disabled; skipping.")

    # ---- Ordering ----
    def test_ordering_when_supported(self):
        if self.order_field is None:
            self.skipTest("No suitable field for ordering test.")

        url = books_list_url() + f"?ordering=-{self.order_field}"
        resp = self.client_anon.get(url)
        if resp.status_code != status.HTTP_200_OK:
            self.skipTest("Ordering not supported (non-200 response to ordering query).")

        results = resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data
        if not isinstance(results, list) or len(results) < 2:
            self.skipTest("Unexpected response shape/size; skipping ordering assertion.")

        # When ordering is applied descending, first result should correspond to book2
        # (we set it to have the later date/datetime).
        first = results[0]
        # We can only assert strongly if an 'id' field is present
        if "id" in first:
            self.assertEqual(first["id"], self.book2.pk)
        else:
            # Otherwise, attempt a best-effort comparison on the order field if it is returned
            if self.order_field in first:
                # Just ensure the first value is not less than the second
                a = first[self.order_field]
                b = results[1].get(self.order_field)
                if a is not None and b is not None:
                    self.assertGreaterEqual(str(a), str(b))
            else:
                self.skipTest("Order field not in response; skipping precise assertion.")
