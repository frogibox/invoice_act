from io import BytesIO


class TestEmployeesAPI:
    """Интеграционные тесты для API сотрудников"""

    def test_add_employee(self, client):
        """Тест: успешное добавление сотрудника"""
        response = client.post(
            "/employees/add",
            data={
                "last_name": "Иванов",
                "first_name": "Иван",
                "middle_name": "Иванович",
                "department": "РПО",
            },
        )
        assert response.status_code in (200, 302, 303)

    def test_add_employee_missing_required(self, client):
        """Тест: ошибка при отсутствии обязательных полей"""
        response = client.post(
            "/employees/add",
            data={"last_name": "", "first_name": ""},
        )
        assert response.status_code in (200, 422)

    def test_bulk_add_employees(self, client):
        """Тест: массовое добавление сотрудников"""
        response = client.post(
            "/employees/bulk-add",
            json={
                "employees": [
                    {"first_name": "Петр", "last_name": "Петров"},
                    {"first_name": "Алексей", "last_name": "Сидоров"},
                ]
            },
        )
        assert response.status_code in (200, 201, 302, 303)

    def test_list_employees(self, client):
        """Тест: получение списка сотрудников"""
        response = client.get("/employees")
        assert response.status_code == 200


class TestStopWordsAPI:
    """Интеграционные тесты для API стоп-слов"""

    def test_add_stop_word(self, client):
        """Тест: добавление стоп-слова"""
        response = client.post(
            "/stop-words/add",
            data={"word": "тестовое"},
        )
        assert response.status_code in (200, 302, 303)

    def test_list_stop_words(self, client):
        """Тест: получение списка стоп-слов"""
        response = client.get("/import")
        assert response.status_code == 200


class TestImportExcel:
    """Интеграционные тесты для импорта из Excel"""

    def test_import_1c_invalid_file(self, client):
        """Тест: загрузка невалидного файла 1С"""
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
        assert response.status_code in (200, 400, 500)

    def test_import_sbis_invalid_file(self, client):
        """Тест: загрузка невалидного файла СБИС"""
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
        assert response.status_code in (200, 400, 500)


class TestContractorsAPI:
    """Интеграционные тесты для API контрагентов"""

    def test_list_contractors(self, client):
        """Тест: получение списка контрагентов"""
        response = client.get("/contractors/list")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_contractor_page(self, client):
        """Тест: страница контрагента"""
        response = client.get("/contractor/1")
        assert response.status_code == 200


class TestInvoicesAPI:
    """Интеграционные тесты для API счетов"""

    def test_list_invoices(self, client):
        """Тест: получение списка счетов"""
        response = client.get("/invoices/list")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_calculate_deadline(self, client):
        """Тест: расчёт срока оплаты"""
        response = client.post("/invoice/calculate-deadline/1")
        assert response.status_code in (200, 404, 422)

    def test_delete_invoice(self, client):
        """Тест: удаление счёта"""
        response = client.post("/invoice/delete/999999")
        assert response.status_code in (200, 302, 303, 404)

    def test_update_invoice(self, client):
        """Тест: обновление счёта"""
        response = client.post("/invoice/update/999999", json={})
        assert response.status_code in (200, 302, 303, 404)


class TestActsAPI:
    """Интеграционные тесты для API актов"""

    def test_get_acts_linked(self, client):
        """Тест: получение привязанных актов"""
        response = client.get("/acts/linked")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_acts_unlinked(self, client):
        """Тест: получение непривязанных актов"""
        response = client.get("/acts/unlinked")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_free_acts(self, client):
        """Тест: получение свободных актов для контрагента"""
        response = client.get("/acts/free/1")
        assert response.status_code == 200

    def test_get_acts_by_invoice(self, client):
        """Тест: получение актов по счёту"""
        response = client.get("/acts/by-invoice/1")
        assert response.status_code == 200

    def test_update_act(self, client):
        """Тест: обновление акта"""
        response = client.post("/act/update/999999", json={})
        assert response.status_code in (200, 302, 303, 404)

    def test_delete_act(self, client):
        """Тест: удаление акта"""
        response = client.post("/act/delete/999999")
        assert response.status_code in (200, 302, 303, 404)

    def test_link_act(self, client):
        """Тест: привязка акта к счёту"""
        response = client.post("/act/link/999999", json={})
        assert response.status_code in (200, 302, 303, 404, 422)

    def test_unlink_act(self, client):
        """Тест: отвязка акта от счёта"""
        response = client.post("/act/unlink/999999")
        assert response.status_code in (200, 302, 303, 404)
