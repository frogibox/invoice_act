import pytest


class TestGetOrCreateContractor:
    """Тесты для функции get_or_create_contractor"""

    def test_create_new_contractor(self, test_session):
        from src.main import get_or_create_contractor

        contractor = get_or_create_contractor(test_session, "ООО Тестовая Компания")
        assert contractor is not None
        assert contractor.id is not None
        assert "тестовая" in contractor.name.lower()

    def test_get_existing_contractor(self, test_session):
        from src.main import get_or_create_contractor
        from src.database import Contractor

        existing = Contractor(name="существующая компания")
        test_session.add(existing)
        test_session.flush()

        found = get_or_create_contractor(test_session, "Существующая Компания")
        assert found.id == existing.id

    def test_create_with_inn(self, test_session):
        from src.main import get_or_create_contractor

        contractor = get_or_create_contractor(
            test_session, "Компания с ИНН", inn="1234567890"
        )
        assert contractor.inn == "1234567890"

    def test_normalization_on_create(self, test_session):
        from src.main import get_or_create_contractor

        contractor = get_or_create_contractor(test_session, 'ООО "Тест" Компания')
        assert "ооо" in contractor.name.lower()

    def test_create_with_none_inn(self, test_session):
        from src.main import get_or_create_contractor

        contractor = get_or_create_contractor(test_session, "Без ИНН", inn=None)
        assert contractor.inn is None


class TestGetOrCreateEmployee:
    """Тесты для функции get_or_create_employee"""

    def test_create_new_employee(self, test_session):
        from src.main import get_or_create_employee

        employee = get_or_create_employee(test_session, "Иван Иванов Иванович")
        assert employee is not None
        assert employee.first_name == "Иван"
        assert employee.last_name == "Иванов"
        assert employee.middle_name == "Иванович"

    def test_get_existing_employee(self, test_session):
        from src.main import get_or_create_employee
        from src.database import Employee

        existing = Employee(first_name="Пётр", last_name="Петров")
        test_session.add(existing)
        test_session.flush()

        found = get_or_create_employee(test_session, "Пётр Петров")
        assert found.id == existing.id

    def test_create_with_two_names(self, test_session):
        from src.main import get_or_create_employee

        employee = get_or_create_employee(test_session, "Сидор Сидоров")
        assert employee.first_name == "Сидор"
        assert employee.last_name == "Сидоров"
        assert employee.middle_name is None

    def test_create_with_one_name(self, test_session):
        from src.main import get_or_create_employee

        employee = get_or_create_employee(test_session, "Только Имя")
        assert employee.first_name == "Только"
        assert employee.last_name == "Имя"

    def test_none_full_name(self):
        from src.main import get_or_create_employee

        result = get_or_create_employee(None, None)
        assert result is None

    def test_empty_full_name(self):
        from src.main import get_or_create_employee

        result = get_or_create_employee(None, "")
        assert result is None

    def test_whitespace_full_name(self, test_session):
        from src.main import get_or_create_employee

        result = get_or_create_employee(test_session, "   ")
        assert result.first_name == ""


class TestCheckEmployeeInComment:
    """Тесты для функции check_employee_in_comment"""

    def test_find_surname_in_comment(self):
        from src.main import check_employee_in_comment

        surnames = {"иванов", "петров", "сидоров"}
        result = check_employee_in_comment(
            "Отправить Иванову на согласование", surnames
        )
        assert result is True

    def test_surname_not_in_comment(self):
        from src.main import check_employee_in_comment

        surnames = {"иванов", "петров"}
        result = check_employee_in_comment("Срочно проверить документ", surnames)
        assert result is False

    def test_case_insensitive(self):
        from src.main import check_employee_in_comment

        surnames = {"иванов"}
        result = check_employee_in_comment("ИВАНОВ должен проверить", surnames)
        assert result is True

    def test_partial_match(self):
        from src.main import check_employee_in_comment

        surnames = {"иванов"}
        result = check_employee_in_comment("Иванович должен проверить", surnames)
        assert result is True

    def test_empty_comment(self):
        from src.main import check_employee_in_comment

        surnames = {"иванов"}
        result = check_employee_in_comment("", surnames)
        assert result is False

    def test_none_comment(self):
        from src.main import check_employee_in_comment

        surnames = {"иванов"}
        result = check_employee_in_comment(None, surnames)
        assert result is False

    def test_empty_surnames(self):
        from src.main import check_employee_in_comment

        result = check_employee_in_comment("Иванов должен проверить", set())
        assert result is False

    def test_multiple_surnames_one_found(self):
        from src.main import check_employee_in_comment

        surnames = {"иванов", "петров", "сидоров"}
        result = check_employee_in_comment("Петров П.П. ответственный", surnames)
        assert result is True


class TestDatabaseModels:
    """Тесты для моделей базы данных"""

    def test_contractor_relationships(self, test_session):
        from src.database import Contractor, Invoice, Act
        from datetime import date, datetime

        contractor = Contractor(name="тест отношений", inn="1234567890")
        test_session.add(contractor)
        test_session.flush()

        invoice = Invoice(
            number="REL-001",
            date=date(2024, 3, 15),
            amount=1000,
            contractor_id=contractor.id,
        )
        act = Act(
            number="ACT-REL-001",
            signing_date=datetime(2024, 3, 20),
            amount=500,
            contractor_id=contractor.id,
        )
        test_session.add_all([invoice, act])
        test_session.commit()

        test_session.expire_all()
        loaded = test_session.query(Contractor).filter_by(id=contractor.id).first()
        assert len(loaded.invoices) == 1
        assert len(loaded.acts) == 1

    def test_invoice_act_relationship(self, test_session):
        from src.database import Contractor, Invoice, Act
        from datetime import date, datetime

        contractor = Contractor(name="инвойс-акт связь")
        test_session.add(contractor)
        test_session.flush()

        invoice = Invoice(
            number="INV-REL",
            date=date(2024, 3, 15),
            amount=1000,
            contractor_id=contractor.id,
        )
        test_session.add(invoice)
        test_session.flush()

        act = Act(
            number="ACT-INV-REL",
            signing_date=datetime(2024, 3, 20),
            amount=1000,
            contractor_id=contractor.id,
            invoice_id=invoice.id,
        )
        test_session.add(act)
        test_session.commit()

        test_session.expire_all()
        loaded_act = test_session.query(Act).filter_by(id=act.id).first()
        assert loaded_act.invoice is not None
        assert loaded_act.invoice.number == "INV-REL"

        loaded_invoice = test_session.query(Invoice).filter_by(id=invoice.id).first()
        assert len(loaded_invoice.acts) == 1

    def test_employee_model(self, test_session):
        from src.database import Employee

        employee = Employee(
            first_name="Тест",
            last_name="Тестов",
            middle_name="Тестович",
            department="РПО",
            position="Менеджер",
        )
        test_session.add(employee)
        test_session.commit()

        loaded = test_session.query(Employee).filter_by(id=employee.id).first()
        assert loaded.first_name == "Тест"
        assert loaded.last_name == "Тестов"
        assert loaded.department == "РПО"

    def test_stop_word_model(self, test_session):
        from src.database import StopWord

        sw = StopWord(word="тестовоеслово")
        test_session.add(sw)
        test_session.commit()

        loaded = test_session.query(StopWord).filter_by(word="тестовоеслово").first()
        assert loaded is not None
        assert loaded.word == "тестовоеслово"

    def test_contractor_unique_name(self, test_session):
        from src.database import Contractor

        c1 = Contractor(name="уникальное имя")
        test_session.add(c1)
        test_session.commit()

        c2 = Contractor(name="уникальное имя")
        test_session.add(c2)
        with pytest.raises(Exception):
            test_session.commit()
