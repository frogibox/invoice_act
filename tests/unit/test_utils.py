from datetime import date, datetime
from src.main import (
    normalize_contractor_name,
    format_contractor_name,
    parse_datetime,
    parse_date,
    parse_amount,
    add_business_days,
    get_russian_holidays,
    is_weekend_or_holiday,
)


class TestNormalizeContractorName:
    """Тесты для функции нормализации имени контрагента"""

    def test_remove_quotes(self):
        assert normalize_contractor_name('ТехноДрайв"СТРОЙ"') == "технодрайв строй"

    def test_remove_extra_spaces(self):
        assert normalize_contractor_name("ТехноДрайв   ООО") == "технодрайв ооо"

    def test_lowercase(self):
        assert normalize_contractor_name("ТехноДрайв ООО") == "технодрайв ооо"

    def test_legal_form_at_end(self):
        result = normalize_contractor_name("ООО ТехноДрайв")
        assert result == "технодрайв ооо"

    def test_complex_name(self):
        result = normalize_contractor_name('ТехноДрайв"СТРОЙ"ООО')
        assert "технодрайв" in result
        assert "ооо" in result

    def test_empty_string(self):
        assert normalize_contractor_name("") == ""

    def test_none_value(self):
        assert normalize_contractor_name(None) is None

    def test_whitespace_only(self):
        assert normalize_contractor_name("   ") == ""

    def test_remove_parentheses_content(self):
        result = normalize_contractor_name("Компания (бывшая) ООО")
        assert "бывшая" not in result
        assert "ооо" in result

    def test_multiple_legal_forms(self):
        result = normalize_contractor_name("ИП Иванов ООО")
        assert "ооо" in result

    def test_all_legal_forms(self):
        legal_forms = [
            "ООО",
            "ИП",
            "АО",
            "ЗАО",
            "ОАО",
            "ПАО",
            "НКО",
            "АНО",
            "ФГУП",
            "МУП",
        ]
        for form in legal_forms:
            result = normalize_contractor_name(f"{form} Компания")
            assert form.lower() in result

    def test_special_quotes(self):
        result = normalize_contractor_name('Company "Test" LLC')
        assert '"' not in result

    def test_semicolon_and_comma(self):
        result = normalize_contractor_name("Компания, Тест; ООО")
        assert "," not in result
        assert ";" not in result


class TestFormatContractorName:
    """Тесты для функции форматирования имени контрагента"""

    def test_capitalize_words(self):
        assert format_contractor_name("технодрайв ооо") == "Технодрайв ООО"

    def test_legal_forms_uppercase(self):
        assert format_contractor_name("ооо техно") == "Техно ООО"
        assert format_contractor_name("ип иванов") == "Иванов ИП"
        assert format_contractor_name("ао компания") == "Компания АО"

    def test_mixed_forms(self):
        result = format_contractor_name("техно стро ооо")
        assert "ООО" in result

    def test_empty_string(self):
        assert format_contractor_name("") == ""

    def test_none_value(self):
        assert format_contractor_name(None) is None

    def test_whitespace_only(self):
        assert format_contractor_name("   ") == ""

    def test_single_word(self):
        assert format_contractor_name("компания") == "Компания"

    def test_already_formatted(self):
        assert format_contractor_name("Компания ООО") == "Компания ООО"

    def test_multiple_legal_forms(self):
        result = format_contractor_name("ип иванов ооо")
        assert "ИП" in result or "ООО" in result


class TestParseDatetime:
    """Тесты для функции парсинга даты и времени"""

    def test_parse_string_date(self):
        result = parse_datetime("15.03.2024")
        assert result is not None
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15

    def test_parse_string_datetime(self):
        result = parse_datetime("15.03.2024 14:30")
        assert result is not None
        assert result.hour == 14
        assert result.minute == 30

    def test_parse_excel_serial_date(self):
        result = parse_datetime(45305)
        assert result is not None
        assert result.year == 2024

    def test_parse_none(self):
        assert parse_datetime(None) is None

    def test_parse_empty_string(self):
        assert parse_datetime("") is None

    def test_parse_invalid_string(self):
        assert parse_datetime("not-a-date") is None

    def test_parse_date_object(self):
        d = date(2024, 3, 15)
        result = parse_datetime(d)
        assert result is not None
        assert result.date() == d

    def test_parse_datetime_object(self):
        dt = datetime(2024, 3, 15, 14, 30)
        result = parse_datetime(dt)
        assert result == dt

    def test_parse_iso_format(self):
        result = parse_datetime("2024-03-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15

    def test_parse_slash_format(self):
        result = parse_datetime("15/03/2024")
        assert result is not None
        assert result.year == 2024

    def test_parse_short_year(self):
        result = parse_datetime("15.03.24 14:30")
        if result is not None:
            assert result.year in (2024, 1924)

    def test_parse_with_seconds(self):
        result = parse_datetime("15.03.2024 14:30:45")
        assert result is not None
        assert result.second == 45

    def test_parse_negative_excel_date(self):
        result = parse_datetime(-1)
        assert result is None or result.year < 1900

    def test_parse_float_excel_date(self):
        result = parse_datetime(45305.5)
        assert result is not None

    def test_parse_whitespace_string(self):
        assert parse_datetime("   ") is None

    def test_parse_time_first_format(self):
        result = parse_datetime("14:30 15.03.2024")
        assert result is not None
        assert result.hour == 14


class TestParseDate:
    """Тесты для функции парсинга даты"""

    def test_parse_string_date(self):
        result = parse_date("15.03.2024")
        assert result == date(2024, 3, 15)

    def test_parse_none(self):
        assert parse_date(None) is None

    def test_parse_empty_string(self):
        assert parse_date("") is None

    def test_parse_datetime_returns_date(self):
        result = parse_date(datetime(2024, 3, 15, 14, 30))
        assert result == date(2024, 3, 15)

    def test_parse_invalid_returns_none(self):
        assert parse_date("invalid") is None


class TestParseAmount:
    """Тесты для функции парсинга суммы"""

    def test_parse_float(self):
        assert parse_amount(100.50) == 100.50

    def test_parse_int(self):
        assert parse_amount(100) == 100.0

    def test_parse_string_with_spaces(self):
        assert parse_amount("1 000,50") == 1000.50

    def test_parse_string_with_comma(self):
        assert parse_amount("100,50") == 100.50

    def test_parse_none(self):
        assert parse_amount(None) is None

    def test_parse_empty_string(self):
        assert parse_amount("") is None

    def test_parse_zero(self):
        assert parse_amount(0) == 0.0

    def test_parse_negative(self):
        assert parse_amount(-100.50) == -100.50

    def test_parse_large_number(self):
        assert parse_amount("1 000 000,00") == 1000000.0

    def test_parse_dot_decimal(self):
        assert parse_amount("100.50") == 100.50

    def test_parse_string_number(self):
        assert parse_amount("500") == 500.0

    def test_parse_invalid_string(self):
        assert parse_amount("abc") is None

    def test_parse_whitespace_only(self):
        assert parse_amount("   ") is None

    def test_parse_very_small(self):
        assert parse_amount(0.01) == 0.01


class TestAddBusinessDays:
    """Тесты для функции добавления рабочих дней"""

    def test_add_simple_days(self):
        start = date(2024, 3, 15)
        holidays = set()
        result = add_business_days(start, 1, holidays)
        assert result == date(2024, 3, 18)

    def test_skip_weekend(self):
        start = date(2024, 3, 15)
        holidays = set()
        result = add_business_days(start, 2, holidays)
        assert result == date(2024, 3, 19)

    def test_zero_days(self):
        start = date(2024, 3, 15)
        holidays = set()
        result = add_business_days(start, 0, holidays)
        assert result == start

    def test_negative_days(self):
        start = date(2024, 3, 15)
        holidays = set()
        result = add_business_days(start, -1, holidays)
        assert result == start

    def test_skip_holiday(self):
        start = date(2024, 3, 7)
        holiday = date(2024, 3, 8)
        holidays = {holiday}
        result = add_business_days(start, 1, holidays)
        assert result != holiday

    def test_multiple_days_with_holidays(self):
        start = date(2024, 3, 6)
        holidays = {date(2024, 3, 8)}
        result = add_business_days(start, 3, holidays)
        assert result > start

    def test_span_weekend(self):
        start = date(2024, 3, 15)
        holidays = set()
        result = add_business_days(start, 5, holidays)
        assert result.weekday() < 5

    def test_large_number_of_days(self):
        start = date(2024, 3, 15)
        holidays = set()
        result = add_business_days(start, 20, holidays)
        assert result > start


class TestIsWeekendOrHoliday:
    """Тесты для функции проверки выходного/праздника"""

    def test_saturday_is_weekend(self):
        d = date(2024, 3, 16)
        assert is_weekend_or_holiday(d, set()) is True

    def test_sunday_is_weekend(self):
        d = date(2024, 3, 17)
        assert is_weekend_or_holiday(d, set()) is True

    def test_weekday_not_weekend(self):
        d = date(2024, 3, 15)
        assert is_weekend_or_holiday(d, set()) is False

    def test_holiday_detected(self):
        d = date(2024, 3, 8)
        holidays = {date(2024, 3, 8)}
        assert is_weekend_or_holiday(d, holidays) is True

    def test_weekday_holiday(self):
        d = date(2024, 1, 1)
        holidays = {date(2024, 1, 1)}
        assert is_weekend_or_holiday(d, holidays) is True

    def test_empty_holidays(self):
        d = date(2024, 3, 15)
        assert is_weekend_or_holiday(d, set()) is False


class TestGetRussianHolidays:
    """Тесты для функции получения праздников России"""

    def test_returns_set(self):
        result = get_russian_holidays(2024)
        assert isinstance(result, set)

    def test_contains_new_year(self):
        result = get_russian_holidays(2024)
        new_years = [d for d in result if d.year == 2024 and d.month == 1]
        assert len(new_years) > 0

    def test_different_years(self):
        holidays_2023 = get_russian_holidays(2023)
        holidays_2024 = get_russian_holidays(2024)
        assert isinstance(holidays_2023, set)
        assert isinstance(holidays_2024, set)

    def test_non_empty(self):
        result = get_russian_holidays(2024)
        assert len(result) > 0

    def test_all_dates_in_year(self):
        result = get_russian_holidays(2024)
        for d in result:
            assert d.year == 2024
