import random
import string


def add_record(page, first_name, last_name, email, age, salary, department):
    page.locator("#addNewRecordButton").click()
    page.locator("#firstName").fill(first_name)
    page.locator("#lastName").fill(last_name)
    page.locator("#userEmail").fill(email)
    page.locator("#age").fill(str(age))
    page.locator("#salary").fill(str(salary))
    page.locator("#department").fill(department)
    page.locator("#submit").click()


def add_random_records(page, num_rows):
    for _ in range(num_rows):
        first_name = "".join(random.choices(string.ascii_letters, k=6))
        last_name = "".join(random.choices(string.ascii_letters, k=8))
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        age = random.randint(18, 65)
        salary = random.randint(2000, 20000)
        department = random.choice(
            ["Engineering", "Legal", "Compliance", "Insurance", "HR", "IT"]
        )
        add_record(page, first_name, last_name, email, age, salary, department)


def test_add_record_to_webtable(page):
    page.goto("https://demoqa.com/webtables")

    # Add a new record
    add_record(page, "John", "Doe", "john.doe@example.com", 35, 7000, "Engineering")

    # Verify that the new record appears in the table
    rows = page.locator(".rt-tr-group")
    found = False
    for i in range(rows.count()):
        row_text = rows.nth(i).inner_text()
        if "John" in row_text and "Doe" in row_text:
            found = True
            break

    assert found, "The new record was not found in the web table"


def test_name_cell_not_empty_in_all_rows(page):
    page.goto("https://demoqa.com/webtables")

    rows = page.locator(".rt-tr-group")
    for i in range(rows.count()):
        row = rows.nth(i)
        # Only check rows that do NOT have the '-padRow' class
        if "-padRow" not in row.locator(".rt-tr").get_attribute("class"):
            first_name_cell = row.locator(".rt-td").nth(0)
            first_name = first_name_cell.inner_text().strip()
            assert first_name != "", f"Row {i+1} has an empty Name cell"
