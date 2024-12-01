let currentItems = [];
// Functionality given by Geoapify https://www.geoapify.com/
function addressAutocomplete(containerElement, callback, options) {
	// create container for input element
  const inputContainerElement = document.createElement("div");
  inputContainerElement.setAttribute("class", "input-container");
  containerElement.appendChild(inputContainerElement);

  // create input element
  const inputElement = document.createElement("input");
  inputElement.setAttribute("type", "text");
  inputElement.setAttribute("placeholder", options.placeholder);
  inputContainerElement.appendChild(inputElement);

  let currentTimeout = null; 
  let currentPromiseReject = null;

  const MIN_ADDRESS_LENGTH = 3;
  const DEBOUNCE_DELAY = 100;

  /* Process a user input: */
  inputElement.addEventListener("input", function(e) {
    const currentValue = this.value;

    // Cancel previous timeout
    if (currentTimeout) {
      clearTimeout(currentTimeout);
    }

    // Cancel previous request promise
    if (currentPromiseReject) {
      currentPromiseReject({
        canceled: true
      });
    }

    // Skip empty or short address strings
    if (!currentValue || currentValue.length < MIN_ADDRESS_LENGTH) {
      return false;
    }

    /* Call the Address Autocomplete API with a delay */
    currentTimeout = setTimeout(() => {
    	currentTimeout = null;
            
      /* Create a new promise and send geocoding request */
      const promise = new Promise((resolve, reject) => {
        currentPromiseReject = reject;

        // Get an API Key on https://myprojects.geoapify.com
        const apiKey = "";

        var url = `https://api.geoapify.com/v1/geocode/autocomplete?text=${encodeURIComponent(currentValue)}&format=json&limit=5&apiKey=${apiKey}`;

        fetch(url)
          .then(response => {
            currentPromiseReject = null;

            // check if the call was successful
            if (response.ok) {
              response.json().then(data => resolve(data));
            } else {
              response.json().then(data => reject(data));
            }
          });
      });

      promise.then((data) => {
        currentItems = data.results;

        /*create a DIV element that will contain the items (values):*/
        const autocompleteItemsElement = document.createElement("div");
        autocompleteItemsElement.setAttribute("class", "autocomplete-items");
        inputContainerElement.appendChild(autocompleteItemsElement);

        /* For each item in the results */
        data.results.forEach((result, index) => {
          /* Create a DIV element for each element: */
          const itemElement = document.createElement("div");
          /* Set formatted address as item value */
          itemElement.innerHTML = result.formatted;
          autocompleteItemsElement.appendChild(itemElement);

          itemElement.addEventListener("click", function(e) {
            inputElement.value = currentItems[index].formatted;
            callback(currentItems[index]);
            /* Close the list of autocompleted values: */
            closeDropDownList();
          });

        });
      }, (err) => {
        if (!err.canceled) {
          console.log(err);
        }
      });
    }, DEBOUNCE_DELAY);
  });  

  /* Focused item in the autocomplete list. This variable is used to navigate with buttons */
  let focusedItemIndex = -1;

  /* Add support for keyboard navigation */
  inputElement.addEventListener("keydown", function(e) {
    var autocompleteItemsElement = containerElement.querySelector(".autocomplete-items");
    if (autocompleteItemsElement) {
      var itemElements = autocompleteItemsElement.getElementsByTagName("div");
      if (e.keyCode == 40) {
        e.preventDefault();
        /*If the arrow DOWN key is pressed, increase the focusedItemIndex variable:*/
        focusedItemIndex = focusedItemIndex !== itemElements.length - 1 ? focusedItemIndex + 1 : 0;
        /*and and make the current item more visible:*/
        setActive(itemElements, focusedItemIndex);
      } else if (e.keyCode == 38) {
        e.preventDefault();

        /*If the arrow UP key is pressed, decrease the focusedItemIndex variable:*/
        focusedItemIndex = focusedItemIndex !== 0 ? focusedItemIndex - 1 : focusedItemIndex = (itemElements.length - 1);
        /*and and make the current item more visible:*/
        setActive(itemElements, focusedItemIndex);
      } else if (e.keyCode == 13) {
        /* If the ENTER key is pressed and value as selected, close the list*/
        e.preventDefault();
        if (focusedItemIndex > -1) {
          closeDropDownList();
        }
      }
    } else {
      if (e.keyCode == 40) {
        /* Open dropdown list again */
        var event = document.createEvent('Event');
        event.initEvent('input', true, true);
        inputElement.dispatchEvent(event);
      }
    }
  });
  
  function setActive(items, index) {
    // More robust null/undefined checking
    if (!items || items.length === 0 || index < 0 || index >= items.length) {
      console.error('Invalid items or index in setActive');
      return false;
    }
  
    // Ensure the item exists and has classList before manipulating it
    try {
      // Reset classes for all items
      for (var i = 0; i < items.length; i++) {
        if (items[i] && items[i].classList) {
          items[i].classList.remove("autocomplete-active");
        }
      }
  
      // Add class "autocomplete-active" to the active element
      if (items[index] && items[index].classList) {
        items[index].classList.add("autocomplete-active");
      }
  
      // Change input value and notify callback
      if (currentItems[index]) {
        inputElement.value = currentItems[index].formatted;
        callback(currentItems[index]);
      }
    } catch (error) {
      console.error('Error in setActive:', error);
    }
  }


  function closeDropDownList() {
    var autocompleteItemsElement = inputContainerElement.querySelector(".autocomplete-items");
    if (autocompleteItemsElement) {
      inputContainerElement.removeChild(autocompleteItemsElement);
    }
    focusedItemIndex = -1;
  }

  document.addEventListener("click", function(e) {
    if (e.target !== inputElement) {
      closeDropDownList();
    } else if (!containerElement.querySelector(".autocomplete-items")) {
      // open dropdown list again
      var event = document.createEvent('Event');
      event.initEvent('input', true, true);
      inputElement.dispatchEvent(event);
    }
  });
}

addressAutocomplete(document.getElementById("autocomplete-container"), (data) => {
  console.log("Selected option: ");
  console.log(data);
}, {
	placeholder: "Enter an address here"
});

document.getElementById("eventForm").addEventListener("submit", function(e) {
  e.preventDefault();  

  
  const addressData = JSON.stringify(currentItems); 

  // Set the hidden input field with the JSON data
  document.getElementById("address-data").value = addressData;

  // Prepare form data manually to ensure all fields are included
  const formData = new FormData(this);
  
  // Add the 'Add Event' marker to ensure correct route handling
  formData.append('Add Event', 'Add Event');

  fetch('/', {
      method: 'POST',
      body: formData
  })
  .then(response => {
      
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      
      return response.text();
  })
  .then(data => {
      
      console.log("Event added successfully");
      
      window.location.reload();
  })
  .catch(error => {
      console.error("Error:", error);
      
      alert("Failed to add event. Please try again.");
  });
});