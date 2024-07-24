import time

import allure
import pytest
from playwright.sync_api import Page

from playwright_tests.core.utilities import Utilities
from playwright_tests.messages.ask_a_question_messages.AAQ_messages.aaq_widget import (
    AAQWidgetMessages)
from playwright_tests.messages.ask_a_question_messages.contact_support_messages import (
    ContactSupportMessages)
from playwright_tests.pages.sumo_pages import SumoPages

troubleshooting_topic_url = ("https://support.allizom.org/en-US/topics/customize-settings-and"
                             "-preferences")


#  C2663958, C2663959
@pytest.mark.exploreByTopics
def test_explore_by_topic_product_filter(page: Page):
    sumo_pages = SumoPages(page)
    utilities = Utilities(page)
    with allure.step("Navigating to the /topics/  Customize settings and preferences  page"):
        utilities.navigate_to_link(troubleshooting_topic_url)
    for topic in sumo_pages.explore_by_topic_page._get_all_topics_side_navbar_options():
        topic = topic.strip()
        if topic != "Customize settings and preferences":
            sumo_pages.explore_by_topic_page._click_on_a_topic_filter(topic)
        with allure.step("Verifying that the correct page header is displayed"):
            assert topic == (sumo_pages.explore_by_topic_page
                             ._get_explore_by_topic_page_header().strip())
        for product in sumo_pages.explore_by_topic_page._get_all_filter_by_product_options():
            product = product.strip()
            if product.strip() == "All Products":
                continue
            else:
                sumo_pages.explore_by_topic_page._select_a_filter_by_product_option(
                    product.strip())
                time.sleep(2)
                # This currently fails due to https://github.com/mozilla/sumo/issues/1901.
                # Uncommenting after the issue is fixed.
                # if not sumo_pages.explore_by_topic_page._get_metadata_of_all_listed_articles():
                #     pytest.fail(f"There is no sublist for {product}")

                for sublist in (sumo_pages.explore_by_topic_page
                                ._get_metadata_of_all_listed_articles()):
                    assert product in sublist


# C2462867
@pytest.mark.exploreByTopics
def test_explore_by_topic_aaq_widget_text(page: Page):
    sumo_pages = SumoPages(page)
    utilities = Utilities(page)

    with allure.step("Signing in to SUMO"):
        utilities.start_existing_session(utilities.username_extraction_from_email(
            utilities.user_secrets_accounts["TEST_ACCOUNT_12"]
        ))

    with allure.step("Navigating to the /topics/  Customize settings and preferences  page"):
        utilities.navigate_to_link(troubleshooting_topic_url)
    for topic in sumo_pages.explore_by_topic_page._get_all_topics_side_navbar_options():
        topic = topic.strip()
        if topic != "Customize settings and preferences":
            sumo_pages.explore_by_topic_page._click_on_a_topic_filter(topic)
        for product in sumo_pages.explore_by_topic_page._get_all_filter_by_product_options():
            product = product.strip()
            sumo_pages.explore_by_topic_page._select_a_filter_by_product_option(product)
            time.sleep(2)
            with allure.step("Verifying the correct AAQ widget text is displayed for products"):
                if product == "All Products":
                    assert (sumo_pages.explore_by_topic_page
                            ._get_text_of_aaq_widget() == AAQWidgetMessages
                            .NEUTRAL_AAQ_SUBHEADING_TEXT)
                elif product in utilities.general_test_data['freemium_products']:
                    assert (sumo_pages.explore_by_topic_page
                            ._get_text_of_aaq_widget() == AAQWidgetMessages
                            .FREEMIUM_AAQ_SUBHEADING_TEXT)
                elif product in utilities.general_test_data['premium_products']:
                    assert (sumo_pages.explore_by_topic_page
                            ._get_text_of_aaq_widget() == AAQWidgetMessages
                            .PREMIUM_AAQ_SUBHEADING_TEXT)
                else:
                    assert not sumo_pages.explore_by_topic_page._is_aaq_text_visible()


# C2663960
@pytest.mark.exploreByTopics
def test_explore_by_topic_aaq_widget_redirect(page: Page):
    sumo_pages = SumoPages(page)
    utilities = Utilities(page)

    with allure.step("Signing in to SUMO"):
        utilities.start_existing_session(utilities.username_extraction_from_email(
            utilities.user_secrets_accounts["TEST_ACCOUNT_12"]
        ))

    with allure.step("Navigating to the /topics/  Customize settings and preferences  page"):
        utilities.navigate_to_link(troubleshooting_topic_url)

    for topic in sumo_pages.explore_by_topic_page._get_all_topics_side_navbar_options():
        topic = topic.strip()
        if topic != "Customize settings and preferences":
            sumo_pages.explore_by_topic_page._click_on_a_topic_filter(topic)
        for product in sumo_pages.explore_by_topic_page._get_all_filter_by_product_options():
            product = product.strip()
            current_url = utilities.get_page_url()
            sumo_pages.explore_by_topic_page._select_a_filter_by_product_option(product)
            print(f"This is the product: {product}")
            time.sleep(2)
            with page.expect_navigation() as navigation_info:
                sumo_pages.explore_by_topic_page._click_on_aaq_continue_button()
            response = navigation_info.value
            assert response.status == 200
            if product == "All Products":
                assert ContactSupportMessages.PAGE_URL == utilities.get_page_url()
            elif product not in utilities.aaq_question_test_data['products_aaq_url']:
                assert (utilities.aaq_question_test_data['product_without_aaq_url'] == utilities.
                        get_page_url())
            else:
                assert (utilities.
                        aaq_question_test_data['products_aaq_url'][product] == utilities.
                        get_page_url())

            utilities.navigate_to_link(current_url)


# C2663961
@pytest.mark.exploreByTopics
def test_incorrect_kb_topic_listing_redirect(page: Page):
    utilities = Utilities(page)
    with page.expect_navigation() as navigation_info:
        utilities.navigate_to_link("https://support.allizom.org/en-US/topics/get-started")
    response = navigation_info.value
    assert response.status == 404
