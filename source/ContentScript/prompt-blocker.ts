// import {browser} from 'webextension-polyfill-ts';

let promptContainer: HTMLDivElement;
let blurOverlay: HTMLDivElement;


function unblockContent(): void {
  // Remove the input field
  promptContainer.remove();
  // Function to apply the blur overlay
  // Move the divs children back into body
  while (blurOverlay.firstChild) {
    document.body.appendChild(blurOverlay.firstChild);
  }
  // Remove the div
  blurOverlay.remove();
  // Reset window onscroll
  window.onscroll = (): void => {};
}

function validatePrompt(prompt: string): boolean {
  const url = 'http://127.0.0.1:5000/validate-reason';
  const data = {
    reason: prompt,
  };

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data), // Convert data to a JSON string
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json(); // Assuming the response is in JSON format
    })
    .then((responseData) => {
      console.log(responseData);
      if (responseData.is_valid) {
        unblockContent();
      }
    })
    .catch((error) => {
      console.error('There was a problem with the fetch operation:', error);
    });
  return false;
}

function makePromptContainer(): HTMLDivElement {

  const container = document.createElement('div');
  container.style.position = 'fixed';
  container.style.top = '50%';
  container.style.left = '50%';
  container.style.transform = 'translate(-50%, -50%)';
  container.style.textAlign = 'center';
  container.style.zIndex = '9999';

  // Create a background container for the tab
  const tabBackground = document.createElement('div');
  tabBackground.style.backgroundColor = '#FF6666'; // Light red background color
  tabBackground.style.width = '100%';
  tabBackground.style.padding = '10px';
  tabBackground.style.borderRadius = '5px 5px 0 0';

  // Create a title for the popup
  const title = document.createElement('div');
  title.textContent = 'Please tell us why you are visiting this website';
  title.style.fontSize = '18px';
  title.style.color = 'white'; // Text color

  // Create a text input field
  const inputField = document.createElement('input');
  inputField.type = 'text';
  inputField.placeholder = 'Type your reason here...';
  inputField.style.padding = '10px';
  inputField.style.fontSize = '16px';
  inputField.style.border = '2px solid #ccc';
  inputField.style.borderRadius = '0 0 5px 5px'; // Rounded bottom corners
  inputField.style.outline = 'none';
  inputField.style.width = '200px';
  inputField.style.marginRight = '5px';
  inputField.style.backgroundColor = 'white'; // White background

  // Create a submit button
  const submitButton = document.createElement('button');
  submitButton.type = 'button';
  submitButton.textContent = 'Submit';
  submitButton.style.padding = '10px 20px';
  submitButton.style.fontSize = '16px';
  submitButton.style.background = '#007bff'; // Blue background
  submitButton.style.color = 'white'; // Text color
  submitButton.style.border = 'none';
  submitButton.style.borderRadius = '5px';
  submitButton.style.cursor = 'pointer';

  // Add event listeners or functionality for the submit button as needed
  submitButton.addEventListener('click', (): void => {
    validatePrompt(inputField.value);
  });

  // Append the title and background to the background container
  tabBackground.appendChild(title);

  // Append the background container, input field, and submit button to the main container
  container.appendChild(tabBackground);
  container.appendChild(inputField);
  container.appendChild(submitButton);

  // Append the container to the document body
  return container;

}

function shouldDisplayPopup(): boolean {
  // Check the current website's URL and decide whether to display the popup
  const currentURL = window.location.href;

  // Define an array of website URLs where you want to display the popup
  const allowedWebsites = [
    'https://www.netflix.com/ie/',
    'https://www.instagram.com/',
    'https://www.tiktok.com/',
    // Add more websites here
    // ...
  ];
  // Check if the currentURL matches any of the allowed websites
  return allowedWebsites.some((website) => currentURL.includes(website));
}

function blockContent(): void {
  if (shouldDisplayPopup()) {
    // make prompt container
    promptContainer = makePromptContainer();
    // Append the input field to the document body
    // Function to apply the blur overlay

    blurOverlay = document.createElement('div');
    blurOverlay.id = 'wrap-blur-overlay';

    // Move the body's children into this wrapper
    while (document.body.firstChild) {
      blurOverlay.appendChild(document.body.firstChild);
    }

    // Append the wrapper to the body
    blurOverlay.style.filter = 'blur(8px)';
    document.body.appendChild(blurOverlay);
    document.body.appendChild(promptContainer);
    const TopScroll = document.documentElement.scrollTop;
    const LeftScroll = document.documentElement.scrollLeft;

    window.onscroll = (): void => {
      window.scrollTo(LeftScroll, TopScroll);
    };
  }
}

export {blockContent, unblockContent};
