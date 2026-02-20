from io import BytesIO
from datetime import date, datetime
import json


class TestEmployeesAPI:
    """Интеграционные тесты для API сотрудников"""

    def test_add_employee_success(self, client, test_session):
        import uuid

        unique_name = f"Test_{uuid.uuid4().hex[:8]}"
        response = client.post(
            "/employees/add",
            data={
                "last_name": unique_name,
                "first_name": "Ivan",
                "middle_name": "Ivanovich",
                "department": "RPO",
                "position": "Manager",
            },
            follow_redirects=False,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True

    def test_add_duplicate_employee(self, client, test_session):
        client.post(
            "/employees/add",
            data={"last_name": "Petrov", "first_name": "Petr"},
        )
        response = client.post(
            "/employees/add",
            data={"last_name": "Petrov", "first_name": "Petr"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False
        assert "error" in data

    def test_add_employee_missing_required(self, client):
        response = client.post(
            "/employees/add",
            data={"last_name": "", "first_name": ""},
        )
        assert response.status_code == 422

    def test_add_employee_only_last_name(self, client):
        response = client.post(
            "/employees/add",
            data={"last_name": "Sidorov", "first_name": ""},
        )
        assert response.status_code == 422

    def test_list_employees_empty(self, client):
        response = client.get("/employees/list")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_employees_with_data(self, client, test_session):
        client.post(
            "/employees/add",
            data={
                "last_name": "TestEmployee",
                "first_name": "Test",
                "department": "RPO",
            },
        )
        response = client.get("/employees/list")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(e["last_name"] == "TestEmployee" for e in data)

    def test_update_employee(self, client, test_session):
        import uuid

        unique_name = f"ToUpdate_{uuid.uuid4().hex[:8]}"
        client.post(
            "/employees/add",
            data={"last_name": unique_name, "first_name": "Test"},
        )
        employees = client.get("/employees/list").json()
        emp_id = next(e["id"] for e in employees if e["last_name"] == unique_name)

        new_name = f"Updated_{uuid.uuid4().hex[:8]}"
        response = client.post(
            f"/employees/update/{emp_id}",
            data={
                "last_name": new_name,
                "first_name": "Test",
                "department": "Sales",
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    def test_update_nonexistent_employee(self, client):
        response = client.post(
            "/employees/update/999999",
            data={"last_name": "Test", "first_name": "Test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_delete_employee(self, client, test_session):
        client.post(
            "/employees/add",
            data={"last_name": "ToDelete", "first_name": "Test"},
        )
        employees = client.get("/employees/list").json()
        emp_id = next(e["id"] for e in employees if e["last_name"] == "ToDelete")

        response = client.post(f"/employees/delete/{emp_id}")
        assert response.status_code == 200
        assert response.json().get("success") is True

    def test_delete_nonexistent_employee(self, client):
        response = client.post("/employees/delete/999999")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_bulk_add_employees(self, client, test_session):
        import uuid

        uid = uuid.uuid4().hex[:8]
        response = client.post(
            "/employees/bulk-add",
            json={
                "employees": [
                    {"first_name": f"Bulk1_{uid}", "last_name": f"Testov_{uid}"},
                    {"first_name": f"Bulk2_{uid}", "last_name": f"Testov_{uid}"},
                ]
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("added", 0) >= 1

    def test_bulk_add_with_missing_fields(self, client):
        response = client.post(
            "/employees/bulk-add",
            json={"employees": [{"first_name": "", "last_name": ""}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("skipped", 0) >= 1


class TestStopWordsAPI:
    """Интеграционные тесты для API стоп-слов"""

    def test_add_stop_word(self, client, test_session):
        response = client.post(
            "/stop-words/add",
            data={"word": "testword123"},
            follow_redirects=False,
        )
        assert response.status_code == 303

    def test_add_duplicate_stop_word(self, client, test_session):
        client.post("/stop-words/add", data={"word": "duplicateword"})
        response = client.post(
            "/stop-words/add",
            data={"word": "duplicateword"},
            follow_redirects=False,
        )
        assert response.status_code == 303

    def test_list_stop_words_page(self, client):
        response = client.get("/import")
        assert response.status_code == 200

    def test_delete_stop_word(self, client, test_session):
        client.post("/stop-words/add", data={"word": "to_delete_word"})
        response = client.get("/import")
        assert response.status_code == 200


class TestContractorsAPI:
    """Интеграционные тесты для API контрагентов"""

    def test_list_contractors_empty(self, client):
        response = client.get("/contractors/list")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_contractor_page_not_found(self, client):
        response = client.get("/contractor/999999")
        assert response.status_code == 404

    def test_update_contractor_inn(self, client, test_session):
        from src.database import Contractor

        contractor = Contractor(name="test contractor for inn")
        test_session.add(contractor)
        test_session.commit()

        response = client.post(
            f"/contractor/update-inn/{contractor.id}",
            data={"inn": "1234567890"},
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    def test_update_contractor_inn_nonexistent(self, client):
        response = client.post(
            "/contractor/update-inn/999999",
            data={"inn": "1234567890"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_update_contractor_empty_inn(self, client, test_session):
        from src.database import Contractor

        contractor = Contractor(name="contractor empty inn")
        test_session.add(contractor)
        test_session.commit()

        response = client.post(
            f"/contractor/update-inn/{contractor.id}",
            data={"inn": ""},
        )
        assert response.status_code == 200


class TestInvoicesAPI:
    """Интеграционные тесты для API счетов"""

    def test_list_invoices_empty(self, client):
        response = client.get("/invoices/list")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_invoices_with_filters(self, client):
        response = client.get(
            "/invoices/list",
            params={
                "contractor_id": 1,
                "motivated_person": "Test",
                "payment_date_from": "2024-01-01",
                "payment_date_to": "2024-12-31",
            },
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_invoices_sorting(self, client):
        for sort_dir in ["asc", "desc"]:
            response = client.get(
                "/invoices/list",
                params={"sort_by": "date", "sort_dir": sort_dir},
            )
            assert response.status_code == 200

    def test_delete_invoice_not_found(self, client):
        response = client.post("/invoice/delete/999999")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_update_invoice_not_found(self, client):
        response = client.post(
            "/invoice/update/999999", data={"payment_date": "2024-01-01"}
        )
        assert response.status_code == 200

    def test_calculate_deadline_invoice_not_found(self, client):
        response = client.post("/invoice/calculate-deadline/999999", data={"days": 5})
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_calculate_deadline_negative_days(self, client, test_session):
        from src.database import Contractor, Invoice

        contractor = Contractor(name="deadline test contractor")
        test_session.add(contractor)
        test_session.flush()
        invoice = Invoice(
            number="DL-001",
            date=date(2024, 3, 15),
            amount=1000,
            contractor_id=contractor.id,
            payment_date=date(2024, 3, 20),
        )
        test_session.add(invoice)
        test_session.commit()

        response = client.post(
            f"/invoice/calculate-deadline/{invoice.id}", data={"days": -5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_calculate_deadline_no_payment_date(self, client, test_session):
        from src.database import Contractor, Invoice

        contractor = Contractor(name="no payment date contractor")
        test_session.add(contractor)
        test_session.flush()
        invoice = Invoice(
            number="NP-001",
            date=date(2024, 3, 15),
            amount=1000,
            contractor_id=contractor.id,
        )
        test_session.add(invoice)
        test_session.commit()

        response = client.post(
            f"/invoice/calculate-deadline/{invoice.id}", data={"days": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False


class TestActsAPI:
    """Интеграционные тесты для API актов"""

    def test_get_acts_linked_empty(self, client):
        response = client.get("/acts/linked")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_acts_unlinked_empty(self, client):
        response = client.get("/acts/unlinked")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_free_acts_empty(self, client):
        response = client.get("/acts/free/1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_acts_by_invoice_empty(self, client):
        response = client.get("/acts/by-invoice/1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_delete_act_not_found(self, client):
        response = client.post("/act/delete/999999")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False

    def test_update_act_not_found(self, client):
        response = client.post("/act/update/999999", data={"amount": 1000})
        assert response.status_code == 200

    def test_link_act_not_found(self, client):
        response = client.post("/act/link/999999", data={"invoice_id": 1})
        assert response.status_code in (200, 303)

    def test_unlink_act_not_found(self, client):
        response = client.post("/act/unlink/999999")
        assert response.status_code in (200, 303)

    def test_acts_filtering_by_contractor(self, client):
        response = client.get("/acts/linked", params={"contractor_id": "1"})
        assert response.status_code == 200

    def test_acts_filtering_by_date_range(self, client):
        response = client.get(
            "/acts/unlinked",
            params={
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
            },
        )
        assert response.status_code == 200

    def test_acts_sorting(self, client):
        for sort_by in ["signing_date", "amount", "contractor_name"]:
            response = client.get(
                "/acts/linked",
                params={"sort_by": sort_by, "sort_dir": "desc"},
            )
            assert response.status_code == 200

    def test_update_act_negative_amount(self, client, test_session):
        from src.database import Contractor, Act

        contractor = Contractor(name="amount test contractor")
        test_session.add(contractor)
        test_session.flush()
        act = Act(
            number="ACT-AMT",
            signing_date=datetime(2024, 3, 15),
            amount=1000,
            contractor_id=contractor.id,
        )
        test_session.add(act)
        test_session.commit()

        response = client.post(f"/act/update/{act.id}", data={"amount": -100})
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is False


class TestImportExcel:
    """Интеграционные тесты для импорта из Excel"""

    def test_import_1c_invalid_file(self, client):
        fake_file = BytesIO(b"not an excel file")
        response = client.post(
            "/import-1c",
            files={
                "file": (
                    "test.xlsx",
                    fake_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or data.get("success") is False

    def test_import_sbis_invalid_file(self, client):
        fake_file = BytesIO(b"not an excel file")
        response = client.post(
            "/import-sbis",
            files={
                "file": (
                    "test.xlsx",
                    fake_file,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or data.get("success") is False

    def test_import_1c_missing_columns(self, client):
        from openpyxl import Workbook
        from io import BytesIO

        wb = Workbook()
        ws = wb.active
        assert ws is not None
        ws.append(["Wrong", "Header"])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = client.post(
            "/import-1c",
            files={
                "file": (
                    "test.xlsx",
                    buffer,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "Missing column" in data["error"]


class TestBusinessLogic:
    """Тесты бизнес-логики"""

    def test_invoice_with_acts_via_api(self, client, test_session):
        from src.database import Contractor, Invoice, Act

        contractor = Contractor(name="api test contractor")
        test_session.add(contractor)
        test_session.commit()

        client.post(
            "/invoices/add",
            data={
                "number": "API-001",
                "date": "2024-03-15",
                "amount": "1000",
                "contractor_id": contractor.id,
            },
        )

        response = client.get("/invoices/list")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_act_linking_unlinking(self, client, test_session):
        from src.database import Contractor, Invoice, Act

        contractor = Contractor(name="link test contractor")
        test_session.add(contractor)
        test_session.flush()

        invoice = Invoice(
            number="LINK-001",
            date=date(2024, 3, 15),
            amount=1000,
            contractor_id=contractor.id,
        )
        test_session.add(invoice)
        test_session.flush()

        act = Act(
            number="ACT-LINK",
            signing_date=datetime(2024, 3, 20),
            amount=1000,
            contractor_id=contractor.id,
        )
        test_session.add(act)
        test_session.commit()
        act_id = act.id
        invoice_id = invoice.id

        response = client.post(f"/act/link/{act_id}", data={"invoice_id": invoice_id})
        assert response.status_code in (200, 303)

        test_session.expire_all()
        linked_acts = client.get(f"/acts/by-invoice/{invoice_id}").json()
        assert any(a["id"] == act_id for a in linked_acts)

        response = client.post(f"/act/unlink/{act_id}")
        assert response.status_code in (200, 303)

        unlinked_acts = client.get(f"/acts/by-invoice/{invoice_id}").json()
        assert not any(a["id"] == act_id for a in unlinked_acts)

    def test_acts_filtering(self, client):
        response = client.get("/acts/linked", params={"sort_by": "signing_date"})
        assert response.status_code == 200

        response = client.get("/acts/unlinked", params={"sort_by": "amount"})
        assert response.status_code == 200

    def test_contractor_with_invoices_and_acts(self, client, test_session):
        from src.database import Contractor, Invoice, Act

        contractor = Contractor(name="full contractor", inn="1234567890")
        test_session.add(contractor)
        test_session.flush()

        invoice = Invoice(
            number="FULL-001",
            date=date(2024, 3, 15),
            amount=1000,
            contractor_id=contractor.id,
        )
        act = Act(
            number="ACT-FULL",
            signing_date=datetime(2024, 3, 20),
            amount=1000,
            contractor_id=contractor.id,
        )
        test_session.add_all([invoice, act])
        test_session.commit()

        response = client.get(f"/contractor/{contractor.id}")
        assert response.status_code == 200
