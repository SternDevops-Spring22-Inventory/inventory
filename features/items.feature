Feature: The inventory tracker service back-end
    As an Inventory Manager
    I need a RESTful catalog service
    So that I can keep track of all my items
Background:
    Given the server is started
Scenario: The server is running
    When I visit the "home page"
    Then I should see "Inventory Tracker REST API Service"
    And  I should not see "404 Not Found"