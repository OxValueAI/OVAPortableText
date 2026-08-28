from __future__ import annotations

import os
import sys
from pathlib import Path


URL = os.environ.get("OVA_EDITOR_URL", "http://127.0.0.1:5173/")
HEADLESS = os.environ.get("OVA_EDITOR_HEADLESS", "").lower() in {"1", "true", "yes"}
CHROME_PATHS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

ZH_OUTLINE = "\u5927\u7eb2"
ZH_VISUAL = "\u53ef\u89c6\u5316"
ZH_MODIFIED = "\u5df2\u4fee\u6539"
ZH_UNDO = "\u64a4\u9500"
ZH_CONTEXT = "\u4e0a\u4e0b\u6587"
ZH_TEXT_BLOCK = "\u6587\u672c\u533a\u5757"


def chrome_binary() -> str | None:
    for path in CHROME_PATHS:
        if path.exists():
            return str(path)
    return None


def run_with_selenium() -> None:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    options = Options()
    binary = chrome_binary()
    if binary:
        options.binary_location = binary
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--new-window")
    options.add_argument("--window-size=1440,1000")

    driver = webdriver.Chrome(options=options)
    try:
        wait = WebDriverWait(driver, 15)
        driver.get(URL)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ova-pte-shell")))
        assert_independent_scroll_selenium(driver)

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ova-pte-locale button:nth-child(2)"))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(normalize-space(), '{ZH_OUTLINE}')]")))
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//button[normalize-space()='{ZH_VISUAL}']")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ova-pte-nav-block")))
        first_block = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ova-pte-nav-block")))
        first_block.click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(normalize-space(), '\u4e0a\u79fb\u533a\u5757')]")))
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(normalize-space(), '{ZH_CONTEXT}')]")))
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(normalize-space(), '{ZH_TEXT_BLOCK}')]")))

        text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ova-pte-focused-editor .ova-pte-inspector-textarea")))
        original_text = text.get_attribute("value") or ""
        text.clear()
        text.send_keys(f"{original_text} smoke")
        wait.until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(normalize-space(), '{ZH_MODIFIED}')]")))
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space()='{ZH_UNDO}']"))).click()
        wait.until(lambda _: text.get_attribute("value") == original_text)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ova-pte-nav-toggle"))).click()
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ova-pte-nav-block")))

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ova-pte-locale button:nth-child(1)"))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, "//button[normalize-space()='Visual']")))
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(normalize-space(), 'Outline')]")))
    finally:
        if HEADLESS:
            driver.quit()


def assert_independent_scroll_selenium(driver) -> None:
    result = driver.execute_script(
        """
        return ['.ova-pte-sidebar', '.ova-pte-editor', '.ova-pte-properties'].map((selector) => {
          const element = document.querySelector(selector);
          const style = window.getComputedStyle(element);
          return {
            selector,
            overflowY: style.overflowY,
            clientHeight: element.clientHeight,
            scrollHeight: element.scrollHeight
          };
        });
        """
    )
    for pane in result:
        assert pane["overflowY"] == "auto", pane
        assert pane["clientHeight"] > 100, pane


def run_with_playwright() -> None:
    from playwright.sync_api import expect, sync_playwright

    binary = chrome_binary()
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=binary,
            headless=HEADLESS,
            args=["--window-size=1440,1000"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(URL)
        page.locator(".ova-pte-shell").wait_for()
        assert_independent_scroll_playwright(page)

        page.locator(".ova-pte-locale button").nth(1).click()
        expect(page.get_by_text(ZH_OUTLINE)).to_be_visible()
        expect(page.get_by_role("button", name=ZH_VISUAL)).to_be_visible()
        expect(page.locator(".ova-pte-nav-block").first).to_be_visible()
        page.locator(".ova-pte-nav-block").first.click()
        expect(page.get_by_text("\u4e0a\u79fb\u533a\u5757").nth(0)).to_be_visible()
        expect(page.get_by_text(ZH_CONTEXT)).to_be_visible()
        expect(page.get_by_text(ZH_TEXT_BLOCK).nth(0)).to_be_visible()

        text = page.locator(".ova-pte-focused-editor .ova-pte-inspector-textarea")
        original_text = text.input_value()
        text.fill(f"{original_text} smoke")
        expect(page.get_by_text(ZH_MODIFIED)).to_be_visible()
        page.get_by_role("button", name=ZH_UNDO).click()
        expect(text).to_have_value(original_text)
        page.locator(".ova-pte-nav-toggle").first.click()
        expect(page.locator(".ova-pte-nav-block").first).to_be_hidden()
        assert_synced_data_rows_playwright(page)
        assert_colspan_table_cells_playwright(page)
        assert_patent_list_blocks_playwright(page)

        page.locator(".ova-pte-locale button").nth(0).click()
        expect(page.get_by_role("button", name="Visual")).to_be_visible()
        expect(page.get_by_text("Outline")).to_be_visible()
        if HEADLESS:
            browser.close()


def assert_independent_scroll_playwright(page) -> None:
    result = page.evaluate(
        """
        ['.ova-pte-sidebar', '.ova-pte-editor', '.ova-pte-properties'].map((selector) => {
          const element = document.querySelector(selector);
          const style = window.getComputedStyle(element);
          return {
            selector,
            overflowY: style.overflowY,
            clientHeight: element.clientHeight,
            scrollHeight: element.scrollHeight
          };
        })
        """
    )
    for pane in result:
        assert pane["overflowY"] == "auto", pane
        assert pane["clientHeight"] > 100, pane


def assert_synced_data_rows_playwright(page) -> None:
    expand_all_sections(page)

    blocks = page.locator(".ova-pte-nav-block")
    for index in range(blocks.count()):
        blocks.nth(index).click()
        row = page.locator(
            ".ova-pte-table-row, .ova-pte-slice-row, .ova-pte-chart-row:not(.ova-pte-chart-head)"
        ).first
        if row.count() == 0:
            continue
        heights = row.evaluate(
            """
            (element) => Array.from(element.querySelectorAll('textarea, input, span'))
              .map((field) => Math.round(field.getBoundingClientRect().height))
            """
        )
        if len(heights) < 2:
            continue
        assert max(heights) - min(heights) <= 1, heights
        return
    raise AssertionError("No editable chart or table data row was found")


def assert_colspan_table_cells_playwright(page) -> None:
    expand_all_sections(page)

    blocks = page.locator(".ova-pte-nav-block")
    for index in range(blocks.count()):
        blocks.nth(index).click()
        colspan = page.locator(".ova-pte-table-row textarea").evaluate_all(
            """
            (fields) => fields.some((field) => field.style.gridColumn.includes('span 2')
              || field.style.gridColumn.includes('span 3')
              || field.style.gridColumn.includes('span 4'))
            """
        )
        if colspan:
            return
    raise AssertionError("No rendered table cell with colSpan was found")


def assert_patent_list_blocks_playwright(page) -> None:
    expand_all_sections(page)

    blocks = page.locator(".ova-pte-nav-block")
    for index in range(blocks.count()):
        blocks.nth(index).click()
        patent_content_visible = page.locator(".ova-pte-table-row textarea").evaluate_all(
            """
            (fields) => fields.some((field) => field.value.includes('Publication (Announcement) No.'))
            """
        )
        if patent_content_visible:
            return
    raise AssertionError("Patent list block cell content was not rendered")


def expand_all_sections(page) -> None:
    for _ in range(8):
        page.evaluate(
            """
            () => Array.from(document.querySelectorAll('.ova-pte-nav-toggle'))
              .filter((button) => !button.disabled && button.textContent.trim() === '+')
              .forEach((button) => button.click())
            """
        )
        page.wait_for_timeout(50)


def main() -> int:
    try:
        run_with_selenium()
        print("browser smoke passed with selenium")
        return 0
    except Exception as selenium_error:
        print(f"selenium unavailable or failed: {selenium_error}", file=sys.stderr)

    try:
        run_with_playwright()
        print("browser smoke passed with playwright")
        return 0
    except Exception as playwright_error:
        print(f"playwright fallback failed: {playwright_error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
