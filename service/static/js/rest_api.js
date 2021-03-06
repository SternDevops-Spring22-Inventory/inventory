$(function () {
  // ****************************************
  //  U T I L I T Y   F U N C T I O N S
  // ****************************************

  // Updates the form with data from the response
  function update_form_data(res) {
    $('#item_id').val(res.id);
    $('#item_name').val(res.name);
    $('#item_category').val(res.category);
    $('#item_quantity').val(res.quantity);
    $('#item_condition').val(res.condition);
  }

  /// Clears all form fields
  function clear_form_data() {
    $('#item_id').val('');
    $('#item_name').val('');
    $('#item_category').val('');
    $('#item_quantity').val('');
    $('#item_condition').val('');
  }

  // Updates the flash message area
  function flash_message(message) {
    $('#flash_message').empty();
    $('#flash_message').append(message);
  }

  // ****************************************
  // Create an Item
  // ****************************************

  $('#create-btn').click(function () {
    let name = $('#item_name').val();
    let category = $('#item_category').val();
    let quantity = $('#item_quantity').val();
    let condition = $('#item_condition').val();

    let data = {
      name: name,
      category: category,
      quantity: parseInt(quantity, 10),
      condition: condition,
    };

    $('#flash_message').empty();

    let ajax = $.ajax({
      type: 'POST',
      url: '/inventory',
      contentType: 'application/json',
      data: JSON.stringify(data),
    });

    ajax.done(function (res) {
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Update an Item
  // ****************************************

  $('#update-btn').click(function () {
    let item_id = $("#item_id").val();
    let name = $('#item_name').val();
    let category = $('#item_category').val();
    let quantity = $('#item_quantity').val();
    let condition = $('#item_condition').val();

    let data = {
      name: name,
      category: category,
      quantity: parseInt(quantity, 10),
      condition: condition,
    };

    $('#flash_message').empty();

    let ajax = $.ajax({
      type: 'PUT',
      url: `/inventory/${item_id}`,
      contentType: 'application/json',
      data: JSON.stringify(data),
    });

    ajax.done(function (res) {
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Retrieve an Item
  // ****************************************

  $('#retrieve-btn').click(function () {
    let item_id = $('#item_id').val();

    $('#flash_message').empty();

    let ajax = $.ajax({
      type: 'GET',
      url: `/inventory/${item_id}`,
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      clear_form_data();
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Delete an Item
  // ****************************************

  $('#delete-btn').click(function () {
    let item_id = $('#item_id').val();

    $('#flash_message').empty();

    let ajax = $.ajax({
      type: 'DELETE',
      url: `/inventory/${item_id}`,
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      clear_form_data();
      flash_message('Item has been Deleted!');
    });

    ajax.fail(function (res) {
      flash_message('Server error!');
    });
  });

  // ****************************************
  // Clear the form
  // ****************************************

  $('#clear-btn').click(function () {
    $('#item_id').val('');
    $('#flash_message').empty();
    clear_form_data();
  });

  // ****************************************
  // Disable an Item
  // ****************************************

  $('#disable-btn').click(function () {
    let item_id = $("#item_id").val();

    $('#flash_message').empty();

    let ajax = $.ajax({
      type: 'PUT',
      url: `/inventory/${item_id}/disable`,
      contentType: 'application/json',
      data: "",
    });

    ajax.done(function (res) {
      update_form_data(res);
      flash_message('Success');
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
    });
  });

  // ****************************************
  // Search for an Item
  // ****************************************

  $('#search-btn').click(function () {
    let name = $('#item_name').val();
    let category = $('#item_category').val();
    let available = $('#item_available').val() == 'true';

    let queryString = '';

    if (name) {
      queryString += 'name=' + name;
    }
    if (category) {
      if (queryString.length > 0) {
        queryString += '&category=' + category;
      } else {
        queryString += 'category=' + category;
      }
    }
    if (available) {
      if (queryString.length > 0) {
        queryString += '&available=' + available;
      } else {
        queryString += 'available=' + available;
      }
    }

    $('#flash_message').empty();

    let ajax = $.ajax({
      type: 'GET',
      url: `/inventory?${queryString}`,
      contentType: 'application/json',
      data: '',
    });

    ajax.done(function (res) {
      //alert(res.toSource())
      $('#search_results').empty();
      let table = '<table class="table table-striped" cellpadding="10">';
      table += '<thead><tr>';
      table += '<th class="col-md-2">ID</th>';
      table += '<th class="col-md-2">Name</th>';
      table += '<th class="col-md-2">Category</th>';
      table += '<th class="col-md-2">Quantity</th>';
      table += '<th class="col-md-2">Condition</th>';
      table += '</tr></thead><tbody>';
      let firstItem = '';
      for (let i = 0; i < res.length; i++) {
        let item = res[i];
        table += `<tr id="row_${i}"><td>${item.id}</td><td>${item.name}</td><td>${item.category}</td><td>${item.quantity}</td><td>${item.condition}</td></tr>`;
        if (i == 0) {
          firstItem = item;
        }
      }
      table += '</tbody></table>';
      $('#search_results').append(table);

      // copy the first result to the form
      if (firstItem != '') {
        update_form_data(firstItem);
      }

      flash_message('Success');
    });

    ajax.fail(function (res) {
      flash_message(res.responseJSON.message);
    });
  });
});
