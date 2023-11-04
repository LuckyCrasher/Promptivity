// import {browser} from 'webextension-polyfill-ts';

let promptContainer: HTMLDivElement;
let blurOverlay: HTMLDivElement;

function validatePrompt(prompt: string): boolean {
  const url = 'https://127.0.0.1/validatePrompt';
  const data = {
    prompt,
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
      console.log(responseData); // Handle the response data here
    })
    .catch((error) => {
      console.error('There was a problem with the fetch operation:', error);
    });
  return false;
}

function makePromptContainer(): HTMLDivElement {
  // Create a container for the input and button
  const container = document.createElement('div');
  container.style.position = 'fixed';
  container.style.top = '50%';
  container.style.left = '50%';
  container.style.transform = 'translate(-50%, -50%)';
  container.style.textAlign = 'center';
  container.style.zIndex = '9999';

  // Create a text input field
  const inputField = document.createElement('input');
  inputField.type = 'text';
  inputField.placeholder = 'Type here...';
  inputField.style.padding = '10px';
  inputField.style.fontSize = '16px';
  inputField.style.border = '2px solid #ccc';
  inputField.style.borderRadius = '5px';
  inputField.style.outline = 'none';
  inputField.style.width = '200px';
  inputField.style.marginRight = '5px';

  // Create a submit button
  const submitButton = document.createElement('button');
  submitButton.type = 'button'; // Use type "button" to prevent form submission
  submitButton.textContent = 'Submit';
  submitButton.style.padding = '10px 20px';
  submitButton.style.fontSize = '16px';
  submitButton.style.background = '#007bff';
  submitButton.style.color = 'white';
  submitButton.style.border = 'none';
  submitButton.style.borderRadius = '5px';
  submitButton.style.cursor = 'pointer';

  // Add event listeners or functionality for the submit button as needed
  submitButton.addEventListener('click', (): void => {
    validatePrompt(inputField.value);
  });

  // Append the input field and submit button to the container
  container.appendChild(inputField);
  container.appendChild(submitButton);

  // Append the container to the document body
  return container;
}

function blockContent(): void {
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

export {blockContent, unblockContent};
