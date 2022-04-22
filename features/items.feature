Feature: The inventory tracker service back-end
    As an Inventory Manager
    I need a RESTful catalog service
    So that I can keep track of all my items

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory RESTful Service" in the title
    And I should not see "404 Not Found"