import re
from playwright.sync_api import sync_playwright
import validators


def main():
    email = ""
    password = ""
    company = ""
    location = ""
    jobTile = ""
    connectLinkList = []
    email = input("Enter the account email: ")
    password = input("Enter the account password: ")
    location = input("Enter the location(exactly how on the web site): ")
    jobTile = input("Enter the job title: ")
    company = input("Enter the company name: ")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        page = context.new_page()
        page.goto("https://www.linkedin.com/")
        page.locator("[data-test-id=\"home-hero-sign-in-cta\"]").click()
        page.get_by_label("Email or phone").fill(email)
        page.get_by_label("Password").click()
        page.get_by_label("Password").fill(password)
        page.get_by_label("Sign in", exact=True).click()
        page.get_by_placeholder("Search", exact=True).click()
        page.get_by_placeholder("Search", exact=True).fill(company)
        page.get_by_placeholder("Search", exact=True).press("Enter")
        page.get_by_role("button", name="People").click()
        page.get_by_label("Locations filter. Clicking").click()
        page.get_by_label("Show all filters. Clicking").click()
        page.get_by_label("Title").click()
        page.get_by_label("Title").fill(jobTile)
        page.get_by_text(company, exact=True).first.click()
        page.get_by_role("button", name="Add a location").click()
        page.get_by_role("combobox", name="Add a location").fill(location)
        page.wait_for_timeout(2000)
        page.get_by_role("combobox", name="Add a location").press("ArrowDown")
        page.get_by_role("combobox", name="Add a location").press("Enter")
        page.get_by_label("Apply current filters to show").click()
        results_text = page.locator("div:not([class]):not([id])", has_text=re.compile(r"\d+ results")).inner_text()
        results_number = int(re.search(r'\d+', results_text).group())
        numberOfPages = results_number // 10
        remainder = results_number % 10
        page.keyboard.press("Tab")
        for a in range(numberOfPages):
            for b in range(10):
                page.keyboard.press("Tab")
                page.wait_for_timeout(400)
                name = page.evaluate("document.activeElement.innerText")
                if name == "LinkedIn Member":
                    continue
                link = page.evaluate("document.activeElement.href")
                page.keyboard.press("Tab")
                page.wait_for_timeout(400)
                button_text = page.evaluate("document.activeElement.innerText")
                if button_text not in ["Message", "Connect", "Follow", "Pending"]:
                    page.keyboard.press("Tab")
                    page.wait_for_timeout(400)
                    button_text = page.evaluate("document.activeElement.innerText")
                if button_text == "":
                    page.keyboard.press("Tab")
                    page.wait_for_timeout(400)
                    button_text = page.evaluate("document.activeElement.innerText")
                if button_text == "Message":
                    connectLinkList.append(link)
                elif button_text == "Connect":
                    page.keyboard.press("Enter")
                    page.get_by_text("Send without a note").click()
                elif button_text == "Follow":
                    connectLinkList.append(link)
                elif button_text == "Pending":
                    continue
                page.wait_for_timeout(500)
            if remainder == 0 and a == numberOfPages - 1:
                break
            page.get_by_label("Next").click()
            page.wait_for_timeout(2000)
        for a in range(remainder):
            page.keyboard.press("Tab")
            page.wait_for_timeout(400)
            name = page.evaluate("document.activeElement.innerText")
            if name == "LinkedIn Member":
                continue
            link = page.evaluate("document.activeElement.href")
            page.keyboard.press("Tab")
            page.wait_for_timeout(400)
            button_text = page.evaluate("document.activeElement.innerText")
            if button_text not in ["Message", "Connect", "Follow", "Pending"]:
                page.keyboard.press("Tab")
                page.wait_for_timeout(400)
                button_text = page.evaluate("document.activeElement.innerText")
            if button_text == "":
                page.keyboard.press("Tab")
                page.wait_for_timeout(400)
                button_text = page.evaluate("document.activeElement.innerText")
            if button_text == "Message":
                connectLinkList.append(link)
            elif button_text == "Connect":
                page.keyboard.press("Enter")
                page.get_by_text("Send without a note").click()
            elif button_text == "Follow":
                connectLinkList.append(link)
            elif button_text == "Pending":
                continue
            page.wait_for_timeout(500)
        page.wait_for_timeout(1000)

        for a in connectLinkList:
            if validators.url(a):
                page.goto(a)
                page.get_by_role("button", name="More actions").click()
                while True:
                    page.keyboard.press("Tab")
                    button_text = page.evaluate("document.activeElement.innerText")
                    if button_text == "Connect":
                        page.keyboard.press("Enter")
                        break
                page.get_by_text("Send without a note").click()
                print("connected")
                page.wait_for_timeout(1000)
        browser.close()


if __name__ == "__main__":
    main()
