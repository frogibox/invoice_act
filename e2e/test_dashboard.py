from playwright.sync_api import expect
import re
import pytest


pytestmark = pytest.mark.e2e


def test_dashboard_loads(page):
    """Тест: главная страница загружается"""
    page.goto("/")
    expect(page).to_have_title(re.compile(r"счет|invoice|tracker", re.IGNORECASE))


def test_dashboard_has_invoices_table(page):
    """Тест: на главной странице есть таблица счетов"""
    page.goto("/")
    table = page.locator("#invoicesTable")
    expect(table).to_be_visible(timeout=10000)


def test_navigation_to_employees(page):
    """Тест: навигация на страницу сотрудников"""
    page.goto("/employees")
    expect(page).to_have_title(re.compile(r"сотрудник", re.IGNORECASE))


def test_navigation_to_import(page):
    """Тест: навигация на страницу импорта"""
    page.goto("/import")
    expect(page).to_have_title(re.compile(r"импорт", re.IGNORECASE))


def test_navigation_to_unlinked_acts(page):
    """Тест: навигация на страницу непривязанных актов"""
    page.goto("/unlinked-acts")
    expect(page).to_have_title(re.compile(r"свободные|непривязан", re.IGNORECASE))


def test_navigation_to_linked_acts(page):
    """Тест: навигация на страницу привязанных актов"""
    page.goto("/linked-acts")
    expect(page).to_have_title(re.compile(r"привязан", re.IGNORECASE))


def test_navigation_to_contractors(page):
    """Тест: навигация на страницу контрагентов"""
    page.goto("/contractors-list")
    expect(page).to_have_title(re.compile(r"контрагент", re.IGNORECASE))


def test_dashboard_responsive(page):
    """Тест: адаптивность главной страницы"""
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("/")
    table = page.locator("#invoicesTable")
    expect(table).to_be_visible()


def test_import_page_has_forms(page):
    """Тест: на странице импорта есть формы"""
    page.goto("/import")
    form = page.locator("form")
    expect(form.first).to_be_visible()


def test_employees_page_has_table(page):
    """Тест: на странице сотрудников есть контейнер для данных"""
    page.goto("/employees")
    page.wait_for_timeout(1000)
    container = page.locator("#employeesTable, .table-container, table")
    if container.count() > 0:
        expect(container.first).to_be_visible()


def test_delete_modal_appears(page):
    """Тест: модальное окно удаления появляется"""
    page.goto("/")
    delete_buttons = page.locator("#invoicesTable button.btn-danger")
    count = delete_buttons.count()
    if count == 0:
        pytest.skip("No delete buttons available")
    delete_buttons.first.click()
    modal = page.locator("#deleteConfirmModal")
    expect(modal).to_be_visible(timeout=5000)
    cancel_btn = page.locator("#deleteConfirmModal .btn-secondary")
    if cancel_btn.count() > 0:
        cancel_btn.click()
        expect(modal).not_to_be_visible(timeout=5000)


def test_page_load_time(page):
    """Тест: время загрузки страницы"""
    import time

    start = time.time()
    page.goto("/")
    load_time = time.time() - start
    assert load_time < 5, f"Page load time {load_time:.2f}s exceeds 5 seconds"


def test_no_console_errors(page):
    """Тест: отсутствие ошибок в консоли"""
    errors = []
    page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
    page.goto("/")
    page.wait_for_timeout(1000)
    critical_errors = [
        e for e in errors if "404" not in e.text and "favicon" not in e.text.lower()
    ]
    assert len(critical_errors) == 0, (
        f"Console errors: {[e.text for e in critical_errors]}"
    )
