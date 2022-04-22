Feature: The inventory tracker service back-end
    As an Inventory Manager
    I need a RESTful catalog service
    So that I can keep track of all my items

Background:
    Given the following items
        | name               | category   | quantity | condition |
        | blue shirt         | shirt      | 1        | NEW       | 
        | black pants        | pants      | 4        | USED      |
        | white socks        | socks      | 10       | NEW       |
        | brown shorts       | shorts     | 3        | USED      |    

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory Demo REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Item 
    When I visit the "Home Page"
    And I set the "Name" to "blue shirt"
    And I set the "Category" to "shirt"
    And I set the "Quantity" to "3"
    And I select "NEW" in the "Condition" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Quantity" field should be empty
    And the "Category" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "blue shirt" in the "Name" field
    And I should see "shirt" in the "Category" field
    And I should see "3" in the "Quantity" field
    And I should see "NEW" in the "Condition" dropdown

Scenario: Update an Item
    When I visit the "Home Page"
    And I set the "Name" to "blue shirt"
    And I press the "Search" button
    Then I should see "blue shirt" in the "Name" field
    And I should see "shirt" in the "Category" field
    When I change "Name" to "white socks"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Item Id" field
    And I press the "Clear" button
    And I paste the "Item Id" field
    And I press the "Retrieve" button
    Then I should see "white socks" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "white socks" in the results
    Then I should not see "blue shirt" in the results